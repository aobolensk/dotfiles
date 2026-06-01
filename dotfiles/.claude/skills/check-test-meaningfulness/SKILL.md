---
name: check-test-meaningfulness
description: Check whether the tests added in the current conversation are meaningful — they fail without the patch and pass with it, and are concise, focused, and regression-catching. Reports verdict per test; does not modify code.
---

# Check Test Meaningfulness

Assess the tests added during this conversation. The core question: does each
new test actually pin down the behavior the patch introduced or fixed?

## Steps

1. Identify the tests added in this conversation and the source change (patch)
   they cover. If either is ambiguous, ask rather than guessing.
2. **Fail-without / pass-with** (the decisive check): confirm each new test
   fails on the pre-patch code and passes on the patched code.
   - Run the test now → it must pass.
   - Temporarily revert ONLY the source change (e.g. `git stash` the non-test
     files, or comment out the fix) and run the test again → it must fail, and
     fail for the *right reason* (the assertion under test, not a setup/import
     error). Restore the source immediately after.
   - If it passes without the patch, the test does not exercise the change —
     flag it as not meaningful.
3. Apply the remaining criteria to each test:
   - **Focused**: exercises one behavior; minimal setup; failure message points
     at a single cause.
   - **Real assertions**: asserts on observable outcomes, not just "runs without
     throwing". No assertion-free tests.
   - **Behavioral, not tautological**: tests the contract, not a copy of the
     implementation. A test that would still pass if the code were wrong (or
     that just re-states the code) is not meaningful.
   - **Deterministic**: no dependence on wall-clock, randomness, network, or
     ordering that could make it flaky.
   - **Non-redundant**: not already covered by an existing test.
   - **Named clearly**: the name describes the scenario/expected outcome.
4. Report a short verdict per test: meaningful / not meaningful / weak, each
   with the one reason that drove the call and a concrete fix if not meaningful.

## Notes

- Read-only assessment. Do NOT modify tests or source; restore any temporary
  revert from step 2 before finishing.
- If the project's test command is unknown, find it before running (CI config,
  README, package manifest) rather than assuming.
