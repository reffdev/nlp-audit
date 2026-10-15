# SPDX-License-Identifier: Apache-2.0
"""Unit tests for audit/quotes.py. Run: python tests/test_quotes.py (or pytest)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "audit"))
from quotes import found, norm  # noqa: E402


def test_relations_are_kept_apart():
    assert not found(r"x \ge y", r"x \le y")
    assert not found(r"x \le y", r"x \ge y")
    assert norm(r"x \le y") != norm(r"x \ge y")


def test_greek_letters_are_kept_apart():
    assert not found(r"\alpha + 1", r"\beta + 1")


def test_latex_and_unicode_agree():
    assert found(r"x \le y", "x ≤ y")
    assert found(r"x \leq y", r"$x\le y$")
    assert found(r"\alpha + 1", "α + 1")


def test_presentation_is_ignored():
    assert found(r"\left( a + b \right)", "(a+b)")
    assert found(r"\mathrm{d}x", "dx")
    assert found(r"C^{m+p+3}_y", r"$C^{m+p+3}_y$")


def test_case_is_kept():
    assert not found("M_alpha", "m_alpha")


def test_unknown_commands_become_tokens():
    assert norm(r"\frac{a}{b}") == "⟨frac⟩ab"
    assert not found(r"\frac{a}{b}", "ab")


if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f()
            print("ok ", name)
