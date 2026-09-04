# FinGuard AI Execution Firewall

## Problem Statement
AI agents making financial decisions (such as granting refunds or approving payouts) can hallucinate, be manipulated via prompt injection, or fail to consider the exact current state of a financial system. Allowing them to execute transactions directly is extremely dangerous. 

## The One Loss Class
The primary objective of the FinGuard Execution Firewall is to completely eliminate one critical loss class: **execution of unverified, out-of-policy, or hallucinated financial actions by autonomous agents.** We treat any incorrect execution as a catastrophic failure.

## Architecture
FinGuard sits between the AI Agent and the Payment Gateway.
- **AI Agent**: Evaluates support conversations and proposes an action (e.g., `APPROVE` a ₹5000 refund).
- **FinGuard Firewall**: Independently pulls the ground truth from the `FinancialRealityEngine`, checks execution policies, verifies evidence, and calculates a risk score using the `RiskEngine`.
- **Test Gateway**: Only executes if FinGuard returns `APPROVE`. If FinGuard returns `REVIEW` or `BLOCK`, execution is prevented.

## Train/Holdout Split & Label-Leakage Bug
- We generated 400 scenarios and stratified them into an 80/20 train/holdout split. The holdout set was augmented with 70 hard, near-boundary cases (total 146 scenarios in holdout).
- **Bug Fixed**: Previously, `FinGuard.evaluate()` suffered from label leakage by directly comparing the agent's proposed action to the ground-truth `expected_decision` field from the dataset. This bypassed all actual logic. The fix removed this leakage, forcing FinGuard to rely strictly on derived financial reality fields (payment amount, already refunded, missing evidence).

## Weighted Risk Model & Auto-Escalation Floor
FinGuard evaluates risk on a 0-100 scale using the following configurable weights:
- State: 25
- Policy: 20
- Evidence: 30
- Behaviour: 15
- Anomaly: 10

**Score mapping**: `0-29` (APPROVE), `30-69` (REVIEW), `70-100` (BLOCK).
**Auto-Escalation**: Severe policy violations or reality mismatches (e.g., requesting a refund greater than the remaining balance) intentionally bypass the weighted sum and force a minimum score of 70 (BLOCK). This fail-safe guarantees that hard constraints are never overridden by "good behaviour" in other areas.

## Final Benchmark
Evaluated on the 146-scenario holdout set containing adversarial cases:

| System | TP | FP | FN | Precision | Recall | FPR | FNR | Accuracy |
|--------|----|----|----|-----------|--------|-----|-----|----------|
| **FinGuard AI Execution Firewall** | 102 | 22 | 0 | 82.26% | 100.00% | 50.00% | 0.00% | 84.93% |
| **Baseline 1: Always Approve** | 0 | 0 | 102 | 0.00% | 0.00% | 0.00% | 100.00% | 30.14% |
| **Baseline 2: Amount Rule (> ₹9,121)** | 14 | 1 | 88 | 93.33% | 13.73% | 2.27% | 86.27% | 39.04% |

## False-Positive Cost
FinGuard produces 22 false positives (genuine SAFE transactions flagged as UNSAFE) out of the holdout set. These are near-boundary `REVIEW` cases deliberately caught by the conservative margin.
- **Cost**: The cost of these false positives is the temporary holding of the refund amount (₹108,230 across the 22 cases) and the manual operational resolution time required for a human operator to clear the review queue. This operational cost is an acceptable trade-off to maintain a 100% recall (zero catastrophic execution failures).

## Synthetic-Data Limitations
- The current dataset is synthetically generated via `scenario_generator.py`. 
- Real-world fraud vectors may be more complex than the generated templates.
- The boundary between `SAFE` and `UNSAFE` is deterministic in the dataset, making 100% recall achievable. Real data may introduce irreducible ambiguity.

## Roadmap (Unbuilt Items)
- **Live Payment Gateway Integration**: Currently mock only.
- **Dynamic Policy Updates**: UI to modify policy rules on the fly.
- **Advanced Graph Analytics**: The Risk Graph UI is currently static mock data.

## Setup / Run Instructions
1. **Backend**: 
   ```bash
   pip install fastapi uvicorn pydantic
   python main.py
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. **Benchmarks**:
   ```bash
   python -m src.benchmark
   python -m src.adversarial_test
   ```
