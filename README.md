# FinGuard — AI Execution Firewall

FinGuard sits between an AI agent's financial decision and its execution. When an AI agent proposes an action — e.g. "Refund customer ₹5,000, 97% confidence" — FinGuard independently verifies that decision against real payment state, policy rules, and evidence before it is allowed to execute. If the AI's decision conflicts with verified reality, FinGuard can override it: APPROVE, REVIEW, or BLOCK.

**Built for:** Razorpay AI Buildathon 2026 — Track 02, AI Risk Manager
**Loss class:** duplicate / excess / policy-violating refund detection
**One-line pitch:** The model can propose. Only the firewall can execute.

---

## The problem

AI agents making financial decisions can be confidently wrong. A refund agent might approve a payment that's already been refunded, exceeds the captured amount, lacks supporting evidence, or fits a fraud pattern — all while reporting high confidence. Blindly executing that decision costs real money. FinGuard exists to catch this failure mode before execution, not after.

---

## How it works

1. An AI agent proposes an action (e.g. refund, amount, confidence).
2. FinGuard independently checks:
   - **Payment state** — is this transition valid? (e.g. already refunded, invalid state)
   - **Policy** — does this violate a defined financial rule?
   - **Evidence** — is the claim supported by evidence, or missing/partial?
   - **Behaviour** — is this consistent with prior activity, or anomalous?
3. Each check contributes to a **weighted risk score**.
4. The score maps to a final decision: **APPROVE / REVIEW / BLOCK**.
5. Every decision produces a reason and an audit log entry — nothing executes silently.

---

## Risk scoring model

The risk score is a weighted, explainable combination of independent signals:

| Factor    | Weight |
|-----------|--------|
| State     | 25     |
| Policy    | 20     |
| Evidence  | 30     |
| Behaviour | 15     |
| Anomaly   | 10     |
| **Total** | **100**|

**Decision thresholds:**
- `0–29` → **APPROVE** — evidence is strong enough to execute automatically.
- `30–69` → **REVIEW** — uncertainty where automatic execution is unsafe but blocking may be premature.
- `70–100` → **BLOCK** — a material contradiction or unacceptable risk exists.

**Auto-escalation floor:** a hard state or reality-check failure (e.g. the transaction is already refunded) forces a BLOCK regardless of the weighted total. This is intentional — factual contradictions are treated as certainties, not probabilistic risk, and are never softened by low scores elsewhere in the model.

---

## Dataset and evaluation methodology

- Synthetic scenarios are generated across 7 base types (`VALID_REFUND`, `ALREADY_REFUNDED`, `REFUND_TOO_LARGE`, `PARTIAL_REFUND`, `MISSING_PAYMENT`, `MISSING_EVIDENCE`, `FALSE_DUPLICATE`) plus a harder tier (near-boundary amounts, partial/ambiguous evidence, conflicting weak signals) designed to avoid trivial separability.
- Dataset was split into a **train set** (used only while building policy rules) and a **held-out test set** (never inspected while writing rules), stratified by scenario type.
- **A label-leakage bug was found and fixed during development:** an early version of the decision engine directly compared the AI's proposed decision to a stored ground-truth label, rather than deriving its verdict independently. This inflated benchmark scores to a suspicious 100% across the board. It was removed — the decision path now derives its verdict only from actual transaction fields (payment amount, refund history, evidence completeness, policy rules), and the ground-truth label is used only afterward, by the benchmark script, to score correctness.

---

## Benchmark results

Held-out test set, 146 scenarios (102 unsafe / 44 safe):

| System | Precision | Recall | FPR | Accuracy | Latency (median) |
|---|---|---|---|---|---|
| **FinGuard** | 82.26% | **100.00%** | 50.00% | 84.93% | 1.25ms |
| Always Approve (naive) | 0.00% | 0.00% | 0.00% | — | ~0ms |
| Amount Rule (threshold only) | — | low | — | — | ~ms range |

*(Amount Rule figures should be re-verified against the live benchmark output before final submission — two slightly different values were produced across development and should be reconciled to one number before presenting.)*

**Why 100% recall matters more than 82% precision here:** FinGuard never let a dangerous refund through, even under adversarial AI proposals that deliberately proposed plausible-but-wrong decisions. Its precision loss comes entirely from one conservative, explainable failure mode — near-boundary refunds get flagged for human review rather than silently auto-approved. In a payments context, we accept this tradeoff deliberately: a false positive costs a customer a short delay; a false negative costs real money.

**False-positive cost:** the 22 false positives on the held-out set correspond to legitimate near-boundary refunds temporarily held for review rather than auto-approved, representing a measurable but bounded operational cost — accepted deliberately to preserve 100% safety recall.

---

## Adversarial testing

Rather than only measuring accuracy on clean scenarios, FinGuard is stress-tested against an adversarial simulator that constructs plausible-but-wrong AI proposals — not naive label flips — including optimistic policy bypasses, false alarms on valid refunds, and near-boundary manipulation. This is strictly a **defensive** testing tool: it exists to validate that FinGuard resists being fooled by a wrong-but-confident AI agent, not to generate attack tooling.

---

## Architecture

```
AI Agent → FinGuard Firewall → Test Gateway
              │
    ┌─────────┼─────────┬───────────┬────────────┐
    ▼         ▼         ▼           ▼            ▼
  State    Policy    Evidence   Behaviour     Risk Score
  Engine    Engine     Check      Signal      (weighted)
    │         │         │           │            │
    └─────────┴─────────┴───────────┴────────────┘
                         ▼
              APPROVE / REVIEW / BLOCK
                         ▼
                   Audit Trail
```

- `src/finguard.py` — core evaluation orchestrator
- `src/reality_engine.py` — payment state / ground-truth verification
- `src/policy_engine.py` — financial rule checks
- `src/risk_engine.py` — weighted risk scoring
- `src/scenario_generator.py` — synthetic dataset generation
- `src/benchmark.py` — held-out precision/recall/latency evaluation
- `src/adversarial_test.py` — adversarial (plausible-wrong) proposal testing
- `main.py` — FastAPI backend, `/api/firewall/evaluate` and dashboard endpoints
- `frontend/` — React dashboard: live decisions feed, review queue, audit trail, benchmarks, risk graph

---

## Running it

```bash
# Backend
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
npm install
npm run dev

# Benchmark
python -m src.benchmark

# Adversarial test
python -m src.adversarial_test
```

---

## Limitations (stated honestly)

- **Synthetic data**: this prototype uses generated synthetic scenarios and does not represent the full distribution of real-world fraud patterns. Real transaction data would surface additional signatures not modeled here.
- **Single loss class**: this build focuses deliberately on refund-decision integrity, not the full space of financial actions (payouts, chargebacks, withdrawals). This was a scope decision to go deep on one class of loss rather than shallow across many.
- **Risk Graph and Red Team Lab UI**: the relationship graph view is illustrative in the current build; the interactive red-team attack simulator is available as a script (`adversarial_test.py`) but disabled as a live UI action in this version.

---

## Roadmap (not built, explicitly out of scope for this submission)

- Full payment relationship graph (customer/device/card/IP fraud-ring detection) beyond the illustrative UI view
- Expansion to additional financial action types (payouts, chargebacks, withdrawals) as separate, independently-evaluated loss classes
- Production-grade REST API for third-party integration
- Broader adversarial coverage and continuous red-teaming
- Real transaction data validation beyond synthetic scenarios

---

## Why this approach

FinGuard doesn't ask "is this transaction fraudulent?" — it asks "should this AI-generated financial action actually be allowed to execute?" That's a narrower, more defensible question, and one that matters increasingly as AI agents are given more autonomy over financial actions. The goal of this build was to answer that question honestly, with real held-out metrics, rather than to build the widest possible feature set.
