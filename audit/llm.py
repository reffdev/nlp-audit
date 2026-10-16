# SPDX-License-Identifier: Apache-2.0
"""Minimal client for an OpenAI-compatible endpoint (vLLM, llama.cpp server, LM Studio, ...).

Configure with environment variables:
  AUDIT_LLM_BASE_URL   default http://127.0.0.1:8000/v1
  AUDIT_LLM_MODEL      model name as the server reports it (default: first model listed)
  AUDIT_LLM_API_KEY    optional
Every request and raw response (including reasoning text, if the server returns it) is appended
to data/llm_raw.jsonl, and successful responses are cached by (model, prompt, sample index) so
reruns never resample silently. Safe to call from several threads.
"""
import hashlib
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "llm_raw.jsonl"
PROMPTS_LOG = ROOT / "data" / "llm_prompts.jsonl"  # full prompt text, once per cache key
_lock = threading.Lock()
_cache = None
_last_finish = {}
RETRY_MAX_TOKENS = 48000  # prompts peak ~67k real tokens; 67k + 48k fits a 131k context
# Server-side limit on concurrent requests (vLLM KV-cache capacity); all threads share it.
# AUDIT_LLM_THINKING=0 turns off reasoning on models whose chat template supports it (Qwen3).
THINKING = os.environ.get("AUDIT_LLM_THINKING", "1") != "0"
# AUDIT_LLM_SAMPLE_OFFSET=k numbers samples k, k+1, ... instead of 0, 1, ...: new seeds (1000 + index) and new
# cache entries, for measuring resampling noise without touching the cached samples of the published run.
SAMPLE_OFFSET = int(os.environ.get("AUDIT_LLM_SAMPLE_OFFSET", "0"))
_slots = threading.BoundedSemaphore(int(os.environ.get("AUDIT_LLM_MAX_CONCURRENCY", "14")))


@lru_cache(maxsize=1)
def client():
    base = os.environ.get("AUDIT_LLM_BASE_URL", "http://127.0.0.1:8000/v1")
    c = OpenAI(base_url=base, api_key=os.environ.get("AUDIT_LLM_API_KEY", "EMPTY"), timeout=1800)
    model = os.environ.get("AUDIT_LLM_MODEL") or c.models.list().data[0].id
    return c, model


def _load_cache():
    global _cache
    with _lock:
        if _cache is None:
            _cache = {}
            if RAW.exists():
                for line in RAW.read_text(encoding="utf-8").splitlines():
                    r = json.loads(line)
                    if r.get("ok"):
                        _cache[(r["key"], r["sample"])] = r["parsed"]
    return _cache


def _one(c, model, key, s, system, user, temperature, max_tokens, tag):
    cache = _load_cache()
    if (key, s) in cache:
        return cache[(key, s)]
    rec = dict(key=key, sample=s, tag=tag, model=model, thinking=THINKING, temperature=temperature,
               max_tokens=max_tokens, run=os.environ.get("AUDIT_RUN_ID", ""), t=time.time())
    try:
        with _slots:
            r = c.chat.completions.create(
                model=model, temperature=temperature, max_tokens=max_tokens, seed=1000 + s,
                response_format={"type": "json_object"},
                extra_body=None if THINKING else {"chat_template_kwargs": {"enable_thinking": False}},
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
        msg = r.choices[0].message
        text = msg.content or ""
        reasoning = getattr(msg, "reasoning_content", None) or getattr(msg, "reasoning", None)
        rec.update(raw=text, reasoning=reasoning, finish_reason=r.choices[0].finish_reason,
                   usage=r.usage.model_dump() if r.usage else None, seconds=round(time.time() - rec["t"], 1))
        try:
            rec["parsed"] = json.loads(text[text.find("{"): text.rfind("}") + 1])
            rec["ok"] = True
        except json.JSONDecodeError as e:
            rec.update(parsed=None, ok=False, error=f"json: {e}")
    except Exception as e:  # network/server errors are recorded, not retried silently
        rec.update(parsed=None, ok=False, error=repr(e))
    with _lock:
        with open(RAW, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if rec.get("ok"):
            _cache[(key, s)] = rec["parsed"]
    _last_finish[(key, s)] = rec.get("finish_reason")
    return rec.get("parsed")


_prompts_lock = threading.Lock()
_prompts_seen = None


def _log_prompt(key, model, system, user, tag):
    """Full prompt text, once per cache key, in PROMPTS_LOG (the raw log stores only the key)."""
    global _prompts_seen
    with _prompts_lock:
        if _prompts_seen is None:
            _prompts_seen = set()
            if PROMPTS_LOG.exists():
                for line in PROMPTS_LOG.open(encoding="utf-8"):
                    try:
                        _prompts_seen.add(json.loads(line)["key"])
                    except (ValueError, KeyError):
                        pass
        if key in _prompts_seen:
            return
        _prompts_seen.add(key)
        with PROMPTS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(dict(key=key, model=model, thinking=THINKING, tag=tag, system=system, user=user),
                               ensure_ascii=False) + "\n")


def complete_json(system, user, samples=3, temperature=0.7, max_tokens=24000, tag=""):
    """Return a list of `samples` parsed JSON objects (None where parsing failed), one per sample.
    max_tokens covers reasoning ("thinking") tokens too on reasoning models."""
    c, model = client()
    # The cache key covers everything that changes the answer: model, reasoning, temperature, token budget and
    # the prompt. Responses logged before v0.2's re-scoring used a key without temperature and budget; they are
    # reused only when AUDIT_LLM_LEGACY_CACHE=1 (to reproduce the published runs from their log).
    key = hashlib.sha256(f"{model}\nthinking={THINKING}\ntemperature={temperature}\nmax_tokens={max_tokens}\n"
                         f"{system}\n{user}".encode()).hexdigest()[:16]
    if os.environ.get("AUDIT_LLM_LEGACY_CACHE") == "1":
        legacy = hashlib.sha256(f"{model}\nthinking={THINKING}\n{system}\n{user}".encode()).hexdigest()[:16]
        cache = _load_cache()
        if all((legacy, s) in cache for s in range(SAMPLE_OFFSET, SAMPLE_OFFSET + samples)):
            return [cache[(legacy, s)] for s in range(SAMPLE_OFFSET, SAMPLE_OFFSET + samples)]
    _log_prompt(key, model, system, user, tag)
    def run(s):
        out = _one(c, model, key, s, system, user, temperature, max_tokens, tag)
        if out is None and _last_finish.get((key, s)) == "length":
            # ran out of tokens mid-reasoning: retry once with a larger budget (same sample seed);
            # both attempts stay in the raw log
            out = _one(c, model, key, s, system, user, temperature, max(RETRY_MAX_TOKENS, 2 * max_tokens),
                       tag + ":retry-long")
        return out
    with ThreadPoolExecutor(samples) as ex:
        return list(ex.map(run, range(SAMPLE_OFFSET, SAMPLE_OFFSET + samples)))


def approx_tokens(s):
    return len(s) // 3
