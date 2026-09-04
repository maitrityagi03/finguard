# FinGuard — AI Execution Firewall

FinGuard sits between an AI agent's financial decision and its execution. When an AI agent proposes an action — for example, "Refund customer ₹5,000, 97% confidence" — FinGuard independently verifies that decision against payment state, policy rules, evidence, and behavioural signals before execution.

If the AI's decision conflicts with verified reality, FinGuard can override it with **APPROVE, REVIEW, or BLOCK**.

**Built for:** Razorpay AI Buildathon 2026 — Track 02, AI Risk Manager  
**Loss class:** Duplicate, excess, or policy-violating refund detection  
**One-line pitch:** **The model can propose. Only the firewall can execute.**

---

## The Problem

AI agents making financial decisions can be confidently wrong.

A refund agent might approve a payment that has already been refunded, request an amount greater than the captured amount, act without supporting evidence, or behave anomalously — while still reporting high confidence.

Allowing an AI agent to execute financial actions directly creates a dangerous failure mode: **a confident AI decision can become a real financial loss.**

FinGuard is designed to catch this failure **before execution**, not after.

---

## How It Works

1. An AI agent proposes a financial action.
2. FinGuard independently verifies the proposal against:
   - **Payment State** — Is the transaction state valid?
   - **Policy** — Does the action violate a financial rule?
   - **Evidence** — Is the claim supported by sufficient evidence?
   - **Behaviour** — Is the action consistent with previous activity?
   - **Anomaly** — Are there unusual signals around the transaction?
3. These signals contribute to an explainable weighted risk score.
4. The score produces a final decision:
   **APPROVE / REVIEW / BLOCK**
5. Every decision generates an explanation and an audit record.
6. The test gateway executes only when FinGuard allows it.

The key principle is:

> **AI proposes. FinGuard decides. The gateway executes only if safe.**

---

## Risk Scoring Model

FinGuard uses a weighted and explainable risk model:

| Factor | Weight |
|---|---:|
| State | 25 |
| Policy | 20 |
| Evidence | 30 |
| Behaviour | 15 |
| Anomaly | 10 |
| **Total** | **100** |

### Decision Thresholds

| Risk Score | Decision |
|---|---|
| 0–29 | **APPROVE** |
| 30–69 | **REVIEW** |
| 70–100 | **BLOCK** |

### Auto-Escalation Floor

A hard state or reality-check failure forces **BLOCK**, regardless of the weighted score.

For example, if a refund is being proposed for a transaction that has already been refunded, the system does not allow other low-risk signals to override that factual contradiction.

This is intentional: **known financial contradictions are treated as hard safety boundaries rather than probabilities.**

---

## Dataset & Evaluation Methodology

FinGuard is evaluated using synthetic transaction scenarios covering seven base types:

- `VALID_REFUND`
- `ALREADY_REFUNDED`
- `REFUND_TOO_LARGE`
- `PARTIAL_REFUND`
- `MISSING_PAYMENT`
- `MISSING_EVIDENCE`
- `FALSE_DUPLICATE`

A harder tier adds near-boundary amounts, partial or ambiguous evidence, and conflicting weak signals to avoid trivial separation.

The dataset is split into:

- **Training set** — used while developing policy rules.
- **Held-out test set** — kept separate from rule development and used only for final evaluation.

### Label-Leakage Bug

During development, an important label-leakage issue was discovered.

An early version of the decision engine directly compared the AI's proposal against the stored ground-truth label. This artificially inflated benchmark performance to approximately 100%.

That logic was removed.

The current decision path derives its verdict independently from transaction information such as:

- payment state
- payment amount
- refund history
- evidence completeness
- policy rules
- behavioural signals

The ground-truth label is used **only by the benchmark evaluator after the decision is produced**.

This makes the evaluation substantially more representative of the actual firewall behaviour.

---

## Benchmark Results

**Held-out test set: 146 scenarios**  
**102 unsafe / 44 safe**

| System | Precision | Recall | FPR | Accuracy | Median Latency |
|---|---:|---:|---:|---:|---:|
| **FinGuard** | **82.26%** | **100.00%** | 50.00% | **84.93%** | **1.25 ms** |
| Always Approve (naive) | 0.00% | 0.00% | 0.00% | — | ~0 ms |

**Confusion matrix — FinGuard**

- True Positives: **102**
- False Positives: **22**
- True Negatives: **22**
- False Negatives: **0**

**P95 latency:** 1.936 ms

### Why Recall Matters

FinGuard achieved **100% recall** on the held-out evaluation, meaning none of the labelled unsafe scenarios were allowed through as safe decisions.

The precision trade-off comes from conservative decisions around legitimate but ambiguous or near-boundary transactions.

In a financial execution setting, this trade-off is deliberate:

> **A false positive creates an operational review cost. A false negative can create an actual financial loss.**

The 22 false positives therefore represent transactions conservatively held for review rather than silently executed.

---

## Adversarial Testing

FinGuard also includes an adversarial testing layer designed to simulate **plausible but incorrect AI proposals**.

The tests cover scenarios such as:

- Over-refund attempts
- Duplicate refunds
- Prompt-injection-style manipulation
- Velocity anomalies
- Device hopping
- AI hallucination

The objective is defensive: test whether the firewall can independently reject a confident but incorrect AI proposal.

The adversarial simulator is not designed to attack real payment systems or generate operational attack tooling.

---

## Architecture

```text
                         AI AGENT
                            │
                            ▼
                     AI PROPOSAL
                            │
                            ▼
              ┌────────────────────────┐
              │       FINGUARD          │
              │   EXECUTION FIREWALL    │
              │                        │
              │  State                 │
              │  Policy                │
              │  Evidence              │
              │  Behaviour             │
              │  Anomaly               │
              │  Risk Score            │
              └───────────┬────────────┘
                          │
                          ▼
                 APPROVE / REVIEW / BLOCK
                          │
                          ▼
                    TEST GATEWAY
                          │
                          ▼
                     AUDIT TRAIL
