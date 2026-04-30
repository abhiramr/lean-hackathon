namespace VerifiedEDA.Retry

inductive AttemptResult where
  | success (proof : String)
  | failure (error : String)
  deriving Repr

structure RetryState where
  attempts_made : Nat
  last_error : Option String
  found_proof : Option String
  deriving Repr

def initRetryState : RetryState :=
  { attempts_made := 0, last_error := none, found_proof := none }

def retryStepSuccess (state : RetryState) (proof : String) : RetryState :=
  { attempts_made := state.attempts_made + 1,
    found_proof := some proof,
    last_error := none }

def retryStepFailure (state : RetryState) (err : String) : RetryState :=
  { attempts_made := state.attempts_made + 1,
    last_error := some err,
    found_proof := state.found_proof }

-- Theorems about individual steps

theorem success_increments (state : RetryState) (proof : String) :
    (retryStepSuccess state proof).attempts_made = state.attempts_made + 1 := by
  unfold retryStepSuccess; rfl

theorem failure_increments (state : RetryState) (err : String) :
    (retryStepFailure state err).attempts_made = state.attempts_made + 1 := by
  unfold retryStepFailure; rfl

theorem success_records_proof (state : RetryState) (proof : String) :
    (retryStepSuccess state proof).found_proof = some proof := by
  unfold retryStepSuccess; rfl

theorem failure_preserves_proof (state : RetryState) (err : String) :
    (retryStepFailure state err).found_proof = state.found_proof := by
  unfold retryStepFailure; rfl

theorem success_clears_error (state : RetryState) (proof : String) :
    (retryStepSuccess state proof).last_error = none := by
  unfold retryStepSuccess; rfl

theorem failure_records_error (state : RetryState) (err : String) :
    (retryStepFailure state err).last_error = some err := by
  unfold retryStepFailure; rfl

-- A success never produces a none proof
theorem success_proof_is_some (state : RetryState) (proof : String) :
    (retryStepSuccess state proof).found_proof.isSome = true := by
  unfold retryStepSuccess; rfl

-- Multiple failures preserve the initial found_proof
theorem two_failures_preserve (state : RetryState) (e1 e2 : String) :
    (retryStepFailure (retryStepFailure state e1) e2).found_proof = state.found_proof := by
  unfold retryStepFailure; rfl

-- After N failures, attempts = initial + N
theorem two_failures_increment (state : RetryState) (e1 e2 : String) :
    (retryStepFailure (retryStepFailure state e1) e2).attempts_made = state.attempts_made + 2 := by
  unfold retryStepFailure; rfl

-- Success after failure still records the proof
theorem failure_then_success (state : RetryState) (err : String) (proof : String) :
    (retryStepSuccess (retryStepFailure state err) proof).found_proof = some proof := by
  unfold retryStepSuccess retryStepFailure; rfl

-- Clean initial state
theorem init_clean :
    initRetryState.attempts_made = 0 ∧
    initRetryState.found_proof = none ∧
    initRetryState.last_error = none := by
  unfold initRetryState; exact ⟨rfl, rfl, rfl⟩

end VerifiedEDA.Retry
