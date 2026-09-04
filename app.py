import streamlit as st
import json
from pathlib import Path

from src.finguard import FinGuard


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FinGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# LOAD DATA
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SCENARIO_FILE = DATA_DIR / "scenarios.json"


def load_scenarios():
    try:
        with open(SCENARIO_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as error:
        st.error("Could not load scenarios.json")
        st.exception(error)
        return []


scenarios = load_scenarios()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🛡️ FinGuard")
    st.caption("Financial AI Safety Platform")

    st.divider()

    st.subheader("Select Mode")

    mode = st.radio(
        "Mode",
        [
            "Transaction Analysis",
            "AI Safety Test"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### FinGuard")

    st.write(
        "An independent safety layer that verifies "
        "AI-generated financial decisions before execution."
    )

    st.divider()

    st.write("🤖 AI proposes")
    st.write("🔎 FinGuard verifies")
    st.write("🛡️ FinGuard decides")


# ============================================================
# MAIN HEADER
# ============================================================

st.title("🛡️ FinGuard")

st.subheader(
    "AI Financial Safety & Verification Layer"
)

st.write(
    "An independent safety layer that verifies "
    "AI-generated financial decisions before execution."
)


# ============================================================
# TRANSACTION ANALYSIS
# ============================================================

if mode == "Transaction Analysis":

    st.divider()

    st.header("🔎 Transaction Analysis")

    st.write(
        "Select a transaction scenario and let the AI propose "
        "a decision. FinGuard independently verifies it."
    )

    st.write("")


    # ========================================================
    # HOW FINGUARD WORKS
    # ========================================================

    st.subheader("How FinGuard Works")

    st.write(
        "FinGuard follows five verification stages before "
        "allowing a financial action."
    )

    st.write("")


    # Use equal-width horizontal columns
    step1, step2, step3, step4, step5 = st.columns(
        [1, 1, 1, 1, 1],
        gap="medium"
    )


    with step1:

        st.markdown("### 01")
        st.markdown("## 🤖")
        st.markdown("**AI Proposal**")
        st.write(
            "AI proposes a financial action."
        )


    with step2:

        st.markdown("### 02")
        st.markdown("## 🔎")
        st.markdown("**Reality Check**")
        st.write(
            "FinGuard verifies financial reality."
        )


    with step3:

        st.markdown("### 03")
        st.markdown("## 📋")
        st.markdown("**Policy Check**")
        st.write(
            "Financial policies are checked."
        )


    with step4:

        st.markdown("### 04")
        st.markdown("## ⚠️")
        st.markdown("**Risk Analysis**")
        st.write(
            "Financial risk is calculated."
        )


    with step5:

        st.markdown("### 05")
        st.markdown("## 🛡️")
        st.markdown("**Final Decision**")
        st.write(
            "FinGuard makes the final decision."
        )


    st.divider()


    # ========================================================
    # TRANSACTION INPUT
    # ========================================================

    st.subheader("Transaction Details")

    if not scenarios:

        st.warning(
            "No scenarios found in data/scenarios.json."
        )

    else:

        scenario_ids = [
            scenario["scenario_id"]
            for scenario in scenarios
            if "scenario_id" in scenario
        ]


        # ----------------------------------------------------
        # INPUTS ALL HORIZONTAL
        # ----------------------------------------------------

        input1, input2, input3 = st.columns(
            [2, 2, 2],
            gap="large"
        )


        with input1:

            scenario_id = st.selectbox(
                "Scenario ID",
                scenario_ids
            )


        selected_scenario = None

        for scenario in scenarios:

            if scenario.get("scenario_id") == scenario_id:

                selected_scenario = scenario
                break


        if selected_scenario:

            default_refund = selected_scenario.get(
                "requested_refund",
                500
            )

        else:

            default_refund = 500


        with input2:

            requested_amount = st.number_input(
                "Requested Refund (₹)",
                min_value=0,
                value=int(default_refund),
                step=100
            )


        with input3:

            st.write("")

            analyze = st.button(
                "🔎 Analyze Transaction",
                type="primary",
                use_container_width=True
            )


        # ====================================================
        # ANALYSIS
        # ====================================================

        if analyze and selected_scenario:

            try:

                guard = FinGuard()


                # ------------------------------------------------
                # SCENARIO DATA
                # ------------------------------------------------

                expected_decision = selected_scenario.get(
                    "expected_decision",
                    "APPROVE"
                )

                scenario_type = selected_scenario.get(
                    "type",
                    "UNKNOWN"
                )


                # ------------------------------------------------
                # SIMULATED AI DECISION
                # ------------------------------------------------

                dangerous_types = [
                    "DUPLICATE_REFUND",
                    "POLICY_VIOLATION",
                    "CONTRADICTION",
                    "MISSING_EVIDENCE",
                    "FINANCIAL_CONTRADICTION"
                ]


                if scenario_type in dangerous_types:

                    ai_decision = "APPROVE"

                else:

                    ai_decision = expected_decision


                evidence_complete = (
                    scenario_type != "MISSING_EVIDENCE"
                )


                # ------------------------------------------------
                # FINGUARD
                # ------------------------------------------------

                result = guard.evaluate(
                    scenario_id=scenario_id,
                    ai_decision=ai_decision,
                    requested_amount=requested_amount,
                    evidence_complete=evidence_complete
                )


                final_decision = result.get(
                    "final_decision",
                    "REVIEW"
                )


                risk_score = result.get(
                    "risk_score",
                    0
                )


                reason = result.get(
                    "reason",
                    "FinGuard completed its verification."
                )


                # =================================================
                # RESULT
                # =================================================

                st.divider()

                st.header("🛡️ FinGuard Decision")


                # -------------------------------------------------
                # METRICS - HORIZONTAL
                # -------------------------------------------------

                m1, m2, m3, m4 = st.columns(
                    [1, 1, 1, 1],
                    gap="medium"
                )


                with m1:

                    st.metric(
                        "AI Recommendation",
                        ai_decision
                    )


                with m2:

                    st.metric(
                        "Requested Refund",
                        f"₹{requested_amount:,.0f}"
                    )


                with m3:

                    st.metric(
                        "Risk Score",
                        str(risk_score)
                    )


                with m4:

                    st.metric(
                        "Final Decision",
                        final_decision
                    )


                st.write("")


                # -------------------------------------------------
                # DECISION MESSAGE
                # -------------------------------------------------

                if final_decision == "BLOCK":

                    st.error(
                        "🔴 BLOCKED — FinGuard prevented "
                        "the proposed financial action."
                    )

                elif final_decision == "APPROVE":

                    st.success(
                        "🟢 APPROVED — FinGuard verified "
                        "the proposed financial action."
                    )

                else:

                    st.warning(
                        "🟡 REVIEW REQUIRED — FinGuard recommends "
                        "human verification."
                    )


                # =================================================
                # VERIFICATION PIPELINE
                # =================================================

                st.subheader(
                    "🔐 Verification Results"
                )


                v1, v2, v3, v4 = st.columns(
                    [1, 1, 1, 1],
                    gap="medium"
                )


                with v1:

                    st.success(
                        "✓ Financial reality checked"
                    )


                with v2:

                    if evidence_complete:

                        st.success(
                            "✓ Evidence complete"
                        )

                    else:

                        st.warning(
                            "⚠ Evidence incomplete"
                        )


                with v3:

                    st.success(
                        "✓ Financial policy checked"
                    )


                with v4:

                    if final_decision == "BLOCK":

                        st.error(
                            "⚠ High-risk action blocked"
                        )

                    elif final_decision == "APPROVE":

                        st.success(
                            "✓ Action approved"
                        )

                    else:

                        st.warning(
                            "⚠ Human review required"
                        )


                # =================================================
                # EXPLANATION
                # =================================================

                st.divider()

                explanation1, explanation2 = st.columns(
                    [1, 1],
                    gap="large"
                )


                with explanation1:

                    st.subheader(
                        "🔎 Why did FinGuard decide this?"
                    )

                    st.info(reason)


                with explanation2:

                    st.subheader(
                        "📋 Transaction Evidence"
                    )

                    st.write(
                        f"**Payment / Scenario ID:** "
                        f"{scenario_id}"
                    )

                    st.write(
                        f"**Scenario Type:** "
                        f"{scenario_type}"
                    )

                    st.write(
                        f"**Expected Decision:** "
                        f"{expected_decision}"
                    )

                    st.write(
                        f"**AI Decision:** "
                        f"{ai_decision}"
                    )

                    st.write(
                        f"**FinGuard Decision:** "
                        f"{final_decision}"
                    )


                # =================================================
                # EVIDENCE TRAIL
                # =================================================

                st.divider()

                st.subheader(
                    "🔍 FinGuard Evidence Trail"
                )

                st.json(result)


                # =================================================
                # ORIGINAL SCENARIO
                # =================================================

                with st.expander(
                    "📄 View Original Transaction Record"
                ):

                    st.json(selected_scenario)


            except Exception as error:

                st.error(
                    "FinGuard could not analyze this transaction."
                )

                st.exception(error)


# ============================================================
# AI SAFETY TEST
# ============================================================

else:

    st.divider()

    st.header("🧪 AI Safety Test")

    st.write(
        "FinGuard deliberately receives incorrect AI decisions "
        "and attempts to detect and correct them."
    )

    st.info(
        "The purpose of this test is to demonstrate that "
        "FinGuard does not blindly trust AI decisions."
    )


    if st.button(
        "🧪 Run AI Safety Test",
        type="primary"
    ):

        try:

            guard = FinGuard()

            total = 0
            corrected = 0

            dangerous = 0
            caught = 0

            results = []


            # ------------------------------------------------
            # TEST EVERY SCENARIO
            # ------------------------------------------------

            for scenario in scenarios:

                scenario_id = scenario.get(
                    "scenario_id"
                )

                expected = scenario.get(
                    "expected_decision",
                    "APPROVE"
                )

                scenario_type = scenario.get(
                    "type",
                    "UNKNOWN"
                )


                # Deliberately make AI wrong

                if expected == "BLOCK":

                    ai_decision = "APPROVE"

                else:

                    ai_decision = "BLOCK"


                requested_amount = scenario.get(
                    "requested_refund",
                    0
                )


                evidence_complete = (
                    scenario_type != "MISSING_EVIDENCE"
                )


                result = guard.evaluate(
                    scenario_id=scenario_id,
                    ai_decision=ai_decision,
                    requested_amount=requested_amount,
                    evidence_complete=evidence_complete
                )


                final_decision = result.get(
                    "final_decision",
                    "REVIEW"
                )


                total += 1


                # ------------------------------------------------
                # CORRECTION
                # ------------------------------------------------

                if final_decision == expected:

                    corrected += 1

                    correction = "CORRECTED"

                else:

                    correction = "NOT CORRECTED"


                # ------------------------------------------------
                # DANGEROUS APPROVAL
                # ------------------------------------------------

                if (
                    expected == "BLOCK"
                    and ai_decision == "APPROVE"
                ):

                    dangerous += 1


                    if final_decision in [
                        "BLOCK",
                        "REVIEW"
                    ]:

                        caught += 1

                        safety = "CAUGHT"

                    else:

                        safety = "MISSED"

                else:

                    safety = "N/A"


                results.append(
                    {
                        "Scenario": scenario_id,
                        "Type": scenario_type,
                        "Expected": expected,
                        "AI Decision": ai_decision,
                        "FinGuard Decision": final_decision,
                        "Correction": correction,
                        "Safety": safety
                    }
                )


            # ------------------------------------------------
            # METRICS
            # ------------------------------------------------

            if total > 0:

                correction_rate = (
                    corrected / total
                ) * 100

            else:

                correction_rate = 0


            if dangerous > 0:

                safety_rate = (
                    caught / dangerous
                ) * 100

            else:

                safety_rate = 0


            # =================================================
            # RESULTS
            # =================================================

            st.divider()

            st.header(
                "📊 AI Safety Test Results"
            )


            r1, r2, r3, r4 = st.columns(
                [1, 1, 1, 1],
                gap="medium"
            )


            with r1:

                st.metric(
                    "Total Scenarios",
                    total
                )


            with r2:

                st.metric(
                    "Corrected Decisions",
                    corrected
                )


            with r3:

                st.metric(
                    "Correction Rate",
                    f"{correction_rate:.1f}%"
                )


            with r4:

                st.metric(
                    "Safety Rate",
                    f"{safety_rate:.1f}%"
                )


            st.divider()


            # =================================================
            # RESULTS TABLE
            # =================================================

            st.subheader(
                "Scenario Results"
            )

            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )


            # =================================================
            # SAFETY SUMMARY
            # =================================================

            st.subheader(
                "🛡️ Safety Summary"
            )


            if dangerous == 0:

                st.info(
                    "No dangerous AI approvals were found."
                )

            elif safety_rate >= 90:

                st.success(
                    f"FinGuard caught {caught} out of "
                    f"{dangerous} dangerous AI approvals."
                )

            else:

                st.warning(
                    f"FinGuard caught {caught} out of "
                    f"{dangerous} dangerous AI approvals."
                )


        except Exception as error:

            st.error(
                "The AI Safety Test failed."
            )

            st.exception(error)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🛡️ FinGuard — AI proposes. FinGuard verifies."
)