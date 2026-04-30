"""
verified_eda/agents/translator.py — Agentic Python→Lean 4 translator.

Uses AST analysis to inspect Python statistical functions and generates
corresponding Lean 4 definitions. Can optionally use an LLM (Claude) for
semantic translation of complex functions.
"""

from __future__ import annotations

import ast
import inspect
import os
import textwrap
from typing import Callable, Optional

# Templates for common statistical operations → Lean 4
LEAN_TEMPLATES = {
    "verified_mean": textwrap.dedent("""\
        /-- Arithmetic mean: sum divided by length. --/
        noncomputable def mean (xs : List ℚ) (h : xs ≠ []) : ℚ :=
          listSum xs / listLen xs
    """),
    "verified_variance": textwrap.dedent("""\
        /-- Population variance: mean of squared deviations. --/
        noncomputable def variance (xs : List ℚ) (h : xs ≠ []) : ℚ :=
          let m := mean xs h
          listSum (sqDiffs xs m) / listLen xs
    """),
    "verified_std": textwrap.dedent("""\
        /-- Standard deviation: square root of variance. --/
        noncomputable def std (xs : List ℚ) (h : xs ≠ []) : ℝ :=
          Real.sqrt (variance xs h)
    """),
    "verified_median": textwrap.dedent("""\
        /-- Median: middle element of sorted list. --/
        noncomputable def median (xs : List ℚ) (h : xs ≠ []) : ℚ :=
          let sorted := xs.mergeSort (· ≤ ·)
          let n := sorted.length
          if n % 2 = 1 then
            sorted.get ⟨n / 2, by omega⟩
          else
            (sorted.get ⟨n / 2 - 1, by omega⟩ + sorted.get ⟨n / 2, by omega⟩) / 2
    """),
    "verified_pearson": textwrap.dedent("""\
        /-- Pearson correlation: covariance / (std_x * std_y). --/
        noncomputable def pearson (xs ys : List ℚ)
            (hx : xs ≠ []) (hy : ys ≠ []) (hlen : xs.length = ys.length) : ℚ :=
          let mx := mean xs hx
          let my := mean ys hy
          let cov := listSum (List.zipWith (fun x y => (x - mx) * (y - my)) xs ys) / listLen xs
          let sx := std xs hx
          let sy := std ys hy
          cov / (sx * sy)
    """),
    "verified_histogram": textwrap.dedent("""\
        /-- Histogram: assign each element to a bin and count. --/
        def assignBins (xs : List ℚ) (binFn : ℚ → ℕ) (nBins : ℕ) : List ℕ :=
          let init := List.replicate nBins 0
          xs.foldl (fun acc x =>
            let idx := min (binFn x) (nBins - 1)
            acc.set idx (acc.get! idx + 1)
          ) init
    """),
}


class TranslatorAgent:
    """
    Agentically translates Python EDA functions into Lean 4 definitions.

    Strategy:
    1. First check if a template exists for the function (fast path).
    2. If no template, parse the Python AST and attempt rule-based translation.
    3. If that fails and an LLM API key is available, use Claude for translation.
    """

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        self._api_key = os.environ.get("ANTHROPIC_API_KEY")

    def translate(self, func: Callable) -> str:
        """Translate a Python function to Lean 4 code."""
        func_name = func.__name__

        # Fast path: use template
        if func_name in LEAN_TEMPLATES:
            return LEAN_TEMPLATES[func_name]

        # Medium path: AST-based translation
        source = inspect.getsource(func)
        lean_code = self._ast_translate(source, func_name)
        if lean_code:
            return lean_code

        # Slow path: LLM translation
        if self.use_llm and self._api_key:
            return self._llm_translate(source, func_name)

        return f"-- TODO: Manual translation needed for {func_name}\nsorry"

    def _ast_translate(self, source: str, func_name: str) -> Optional[str]:
        """Attempt rule-based AST translation."""
        try:
            tree = ast.parse(textwrap.dedent(source))
            func_def = tree.body[0]
            if not isinstance(func_def, ast.FunctionDef):
                return None

            # Extract parameter info
            params = [arg.arg for arg in func_def.args.args]
            param_str = " ".join(
                f"({p} : List ℚ)" if p == "data" else f"({p} : ℚ)"
                for p in params
                if p != "self"
            )

            return textwrap.dedent(f"""\
                /-- Auto-translated from Python: {func_name} --/
                noncomputable def {func_name.replace('verified_', '')} {param_str} : ℚ :=
                  sorry -- Proof obligation: implement in Lean 4
            """)

        except Exception:
            return None

    def _llm_translate(self, source: str, func_name: str) -> str:
        """Use Groq LLM for semantic translation."""
        try:
            import requests

            api_key = ""
            if not api_key:
                return f"-- GROQ_API_KEY not set\nsorry"

            prompt = textwrap.dedent(f"""\
                You are a formal methods expert. Translate this Python function
                into an equivalent Lean 4 definition.

                Rules:
                1. Use List Int as the data type
                2. Match the mathematical semantics exactly
                3. Add noncomputable if division is used
                4. Include a docstring

                Python:
                {source}

                Respond with ONLY the Lean 4 code, no explanation.
            """)

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                    "temperature": 0.2,
                },
                timeout=30,
            )

            if response.status_code != 200:
                return f"-- Groq API error: {response.status_code}\nsorry"

            lean_code = response.json()["choices"][0]["message"]["content"].strip()
            lean_code = lean_code.replace("```lean", "").replace("```", "").strip()

            if "def " in lean_code or "theorem " in lean_code:
                return lean_code
            return f"-- Groq translation for {func_name} (needs review)\n{lean_code}"

        except Exception as e:
            return f"-- Groq translation failed: {e}\nsorry"

    def translate_all(self, functions: list[Callable]) -> str:
        """Translate multiple functions and combine into a Lean module."""
        parts = [
            "import Mathlib.Data.List.Basic",
            "import Mathlib.Tactic",
            "",
            "namespace VerifiedEDA",
            "",
        ]
        for func in functions:
            parts.append(self.translate(func))
            parts.append("")

        parts.append("end VerifiedEDA")
        return "\n".join(parts)
