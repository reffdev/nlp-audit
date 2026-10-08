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
_lock = threading.Lock()
_cache = None
_last_finish = {}
RETRY_MAX_TOKENS = 48000  # prompts peak ~67k real tokens; 67k + 48k fits a 131k context
# Server-side limit on concurrent requests (vLLM KV-cache capacity); all threads share it.
# AUDIT_LLM_THINKING=0 turns off reasoning on models whose chat template supports it (Qwen3).
THINKING = os.environ.get("AUDIT_LLM_THINKING", "1") != "0"
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
    rec = dict(key=key, sample=s, tag=tag, model=model, thinking=THINKING, t=time.time())
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


def complete_json(system, user, samples=3, temperature=0.7, max_tokens=24000, tag=""):
    """Return a list of `samples` parsed JSON objects (None where parsing failed), one per sample.
    max_tokens covers reasoning ("thinking") tokens too on reasoning models."""
    c, model = client()
    key = hashlib.sha256(f"{model}\nthinking={THINKING}\n{system}\n{user}".encode()).hexdigest()[:16]
    def run(s):
        out = _one(c, model, key, s, system, user, temperature, max_tokens, tag)
        if out is None and _last_finish.get((key, s)) == "length":
            # ran out of tokens mid-reasoning: retry once with a larger budget (same sample seed);
            # both attempts stay in the raw log
            out = _one(c, model, key, s, system, user, temperature, max(RETRY_MAX_TOKENS, 2 * max_tokens),
                       tag + ":retry-long")
        return out
    with ThreadPoolExecutor(samples) as ex:
        return list(ex.map(run, range(samples)))


def approx_tokens(s):
    return len(s) // 3
