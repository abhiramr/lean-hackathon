import VerifiedEDA.Defs
import VerifiedEDA.Proofs

namespace VerifiedEDA

theorem innerProd_nil_left (ys : List Int) :
    innerProd [] ys = 0 := by
  simp [innerProd]

theorem innerProd_nil_right (xs : List Int) :
    innerProd xs [] = 0 := by
  cases xs with
  | nil => simp [innerProd]
  | cons x xs => simp [innerProd]

theorem sqDiffs_length (xs : List Int) (c : Int) :
    (sqDiffs xs c).length = xs.length := by
  simp [sqDiffs]

theorem binTotal_cons (x : Nat) (xs : List Nat) :
    binTotal (x :: xs) = x + binTotal xs := by
  rfl

end VerifiedEDA
