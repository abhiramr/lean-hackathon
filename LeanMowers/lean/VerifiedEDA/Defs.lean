/-
  VerifiedEDA/Defs.lean — Core mathematical definitions.
  Self-contained: no Mathlib dependency.
  All proofs use only Lean 4 built-in tactics.
-/

namespace VerifiedEDA

-- ══════════════════════════════════════════════════════════════
-- § 1. List Utilities (over Float for simplicity, Int for proofs)
-- ══════════════════════════════════════════════════════════════

/-- Sum of a list of integers. Mirrors Python's `sum(data)`. -/
def listSum : List Int → Int
  | [] => 0
  | (x :: xs) => x + listSum xs

/-- Length of a list as a natural number. -/
def listLen : List Int → Nat
  | [] => 0
  | (_ :: xs) => 1 + listLen xs

/-- Squared difference: (x - c)^2. Always non-negative. -/
def sqDiff (x c : Int) : Int := (x - c) * (x - c)

/-- Map each element to its squared difference from a center value. -/
def sqDiffs (xs : List Int) (c : Int) : List Int :=
  xs.map (fun x => sqDiff x c)

/-- Inner product (dot product) of two lists. -/
def innerProd : List Int → List Int → Int
  | [], _ => 0
  | _, [] => 0
  | (x :: xs), (y :: ys) => x * y + innerProd xs ys

/-- Total count across histogram bins. -/
def binTotal : List Nat → Nat
  | [] => 0
  | (c :: cs) => c + binTotal cs

end VerifiedEDA
