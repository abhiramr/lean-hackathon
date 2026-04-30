import VerifiedEDA.Defs

namespace VerifiedEDA

theorem listSum_append (xs ys : List Int) :
    listSum (xs ++ ys) = listSum xs + listSum ys := by
  induction xs with
  | nil => simp [listSum]
  | cons x xs ih =>
    simp [listSum, ih]
    omega

theorem listSum_singleton (x : Int) :
    listSum [x] = x := by
  simp [listSum]

theorem listSum_nil : listSum [] = (0 : Int) := by
  rfl

theorem listLen_pos (xs : List Int) (h : xs ≠ []) :
    0 < listLen xs := by
  cases xs with
  | nil => exact absurd rfl h
  | cons x xs =>
    simp [listLen]
    omega

theorem listLen_append (xs ys : List Int) :
    listLen (xs ++ ys) = listLen xs + listLen ys := by
  induction xs with
  | nil => simp [listLen]
  | cons x xs ih =>
    simp [listLen, ih]
    omega

theorem sqDiff_nonneg (x c : Int) : 0 ≤ sqDiff x c := by
  sorry


theorem listSum_nonneg (xs : List Int)
    (h : ∀ x ∈ xs, 0 ≤ x) :
    0 ≤ listSum xs := by
  induction xs with
  | nil => simp [listSum]
  | cons x xs ih =>
    simp [listSum]
    have hx : 0 ≤ x := h x (List.mem_cons_self x xs)
    have hxs : 0 ≤ listSum xs := by
      apply ih
      intro y hy
      exact h y (List.mem_cons_of_mem x hy)
    omega

theorem innerProd_self_nonneg (xs : List Int) :
    0 ≤ innerProd xs xs := by
  sorry


theorem binTotal_append (xs ys : List Nat) :
    binTotal (xs ++ ys) = binTotal xs + binTotal ys := by
  induction xs with
  | nil => simp [binTotal]
  | cons x xs ih =>
    simp [binTotal, ih]
    omega

theorem binTotal_nil : binTotal [] = 0 := by
  rfl

theorem binTotal_replicate_zero (n : Nat) :
    binTotal (List.replicate n 0) = 0 := by
  induction n with
  | zero => simp [binTotal]
  | succ n ih =>
    simp [List.replicate, binTotal, ih]

end VerifiedEDA
