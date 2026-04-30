import VerifiedEDA.Agent

namespace VerifiedEDA.Agent

theorem prover_always_marks (r : VerifiedResult) (success : Bool) :
    (proverStep r success).prover_ran = true := by
  unfold proverStep; rfl

theorem proven_requires_prover (r : VerifiedResult) (success : Bool) :
    (proverStep r success).status = .proven →
    (proverStep r success).prover_ran = true := by
  intro _; unfold proverStep; rfl

theorem failed_proof_gives_failed_status (r : VerifiedResult) :
    (proverStep r false).status = .failed := by
  unfold proverStep; rfl

theorem successful_proof_gives_proven_status (r : VerifiedResult) :
    (proverStep r true).status = .proven := by
  unfold proverStep; rfl

theorem certifier_requires_prover (r : VerifiedResult)
    (h : r.prover_ran = false) :
    (certifierStep r).certifier_ran = r.certifier_ran := by
  unfold certifierStep; simp [h]

theorem certifier_certifies_after_prover (r : VerifiedResult)
    (h : r.prover_ran = true) :
    (certifierStep r).certifier_ran = true := by
  unfold certifierStep; simp [h]

theorem certifier_preserves_status (r : VerifiedResult) :
    (certifierStep r).status = r.status := by
  unfold certifierStep; split <;> rfl

theorem pipeline_prover_ran (r : VerifiedResult) (success : Bool) :
    (runPipeline r success).prover_ran = true := by
  unfold runPipeline certifierStep proverStep; simp

theorem pipeline_certifier_ran (r : VerifiedResult) (success : Bool) :
    (runPipeline r success).certifier_ran = true := by
  unfold runPipeline certifierStep proverStep; simp

theorem pipeline_success_gives_proven (r : VerifiedResult) :
    (runPipeline r true).status = .proven := by
  unfold runPipeline certifierStep proverStep; simp

theorem pipeline_failure_gives_failed (r : VerifiedResult) :
    (runPipeline r false).status = .failed := by
  unfold runPipeline certifierStep proverStep; simp

theorem pipeline_increments_attempts (r : VerifiedResult) (success : Bool) :
    (runPipeline r success).attempts = r.attempts + 1 := by
  unfold runPipeline certifierStep proverStep; simp

theorem pipeline_proven_implies_certified (r : VerifiedResult) (success : Bool) :
    (runPipeline r success).status = .proven →
    (runPipeline r success).certifier_ran = true := by
  intro _; exact pipeline_certifier_ran r success

theorem pending_result_clean (op : String) (val : Int) :
    (mkPendingResult op val).prover_ran = false ∧
    (mkPendingResult op val).certifier_ran = false ∧
    (mkPendingResult op val).status = .pending := by
  unfold mkPendingResult; exact ⟨rfl, rfl, rfl⟩

end VerifiedEDA.Agent
