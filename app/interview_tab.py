# ================================================================
# interview_tab.py
# Streamlit UI runner for timed per-question interview
# (Updated: rubric display + clean scorecard + completion breakdown table)
# ================================================================

import streamlit as st

from interview_engine import (
    generate_interview_plan,
    evaluate_answer,
    compute_interview_score,
    now_ts,
)


def _get_or_init_interview_state(job, cand_idx: int):
    cand = job["candidates"][cand_idx]
    if "interview" not in cand or not isinstance(cand["interview"], dict):
        cand["interview"] = {
            "status": "not_started",
            "plan": None,
            "q_index": 0,
            "q_started_at": None,
            "answers": [],
            "final": None,
        }
    return cand["interview"]


def _render_rubric(expected_points):
    st.markdown("### How this will be graded (rubric)")
    expected_points = expected_points or []
    if expected_points:
        for p in expected_points:
            st.write("•", p)
    else:
        st.write("— No rubric points provided.")


def _render_scorecard(eval_out: dict):
    st.markdown("### Answer rating")

    score = eval_out.get("score_0_to_5", 0)
    st.write("**Score:**", f"{score}/5")
    st.write("**Time penalty applied:**", "Yes" if eval_out.get("time_penalty_applied") else "No")

    covered = eval_out.get("covered_points", []) or []
    missing = eval_out.get("missing_points", []) or []

    st.markdown("**Covered points:**")
    if covered:
        for c in covered:
            st.write("✅", c)
    else:
        st.write("—")

    st.markdown("**Missing points:**")
    if missing:
        for m in missing:
            st.write("⚠️", m)
    else:
        st.write("—")

    fb = (eval_out.get("feedback") or "").strip()
    if fb:
        st.markdown("**Feedback:**")
        st.write(fb)


def _render_completed_breakdown(interview: dict, candidate_name: str):
    answers = interview.get("answers", []) or []
    final = interview.get("final", {}) or {}

    st.write("## ✅ Interview Completed")
    st.caption(f"Candidate: {candidate_name}")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Answered", str(len(answers)))
    with col2:
        avg_5 = final.get("average_0_to_5")
        st.metric("Average", f"{avg_5:.2f}/5" if isinstance(avg_5, (int, float)) else "—")
    with col3:
        score_100 = final.get("interview_score")
        st.metric("Score", f"{score_100:.1f}/100" if isinstance(score_100, (int, float)) else "—")
    with col4:
        timed_out_count = sum(1 for a in answers if a.get("timed_out"))
        st.metric("Timed out", str(timed_out_count))

    # Breakdown table
    st.write("### Per-question breakdown")
    rows = []
    for a in answers:
        qid = a.get("question_id")
        rows.append(
            {
                "Q#": qid,
                "Skill": a.get("skill"),
                "Difficulty": a.get("difficulty"),
                "Score (/5)": a.get("score_0_to_5"),
                "Time taken (s)": a.get("time_taken_sec"),
                "Limit (s)": a.get("time_limit_sec"),
                "Timed out": a.get("timed_out"),
                "Time penalty": a.get("time_penalty_applied"),
                "Feedback": (a.get("feedback") or "").strip(),
            }
        )

    # Streamlit can render list-of-dicts directly
    st.dataframe(rows, use_container_width=True, hide_index=True)

    # Optional: show answers + rubric coverage
    with st.expander("Details: answers + covered/missing points", expanded=False):
        for a in answers:
            st.markdown(f"#### Q{a.get('question_id')} — {a.get('skill')} ({a.get('score_0_to_5')}/5)")
            st.write("**Question:**", a.get("question_text", "—"))
            st.write("**Answer:**", a.get("answer_text", ""))
            st.write("**Covered:**", a.get("covered_points", []) or [])
            st.write("**Missing:**", a.get("missing_points", []) or [])
            st.write("—")


def render_interview_tab(job, jid: str):
    st.subheader("🧠 Timed AI Interview (per question)")

    if not job:
        st.info("Select a job first.")
        return

    if not job.get("ai_jd"):
        st.warning("Parse the JD first (Jobs tab).")
        return

    if not job.get("candidates"):
        st.info("Upload & parse resumes first (Candidates tab).")
        return

    # Only show candidates that have scoring results
    scored = []
    for i, c in enumerate(job["candidates"]):
        if c.get("scoring"):
            scored.append((i, c))

    if not scored:
        st.info("Compute scores first (Scoring tab).")
        return

    # Candidate selector
    labels = []
    for i, c in scored:
        sc = c["scoring"]
        skill_pct = sc.get("skill_match_percent", 0)
        ai_score  = sc.get("ai_semantic_score", 0)
        fit = sc.get("ai_semantic_fit") or ("Strong" if ai_score >= 80 else "Moderate" if ai_score >= 50 else "Weak")
        labels.append(
            f"{c['name']} | Skill Match {sc.get('skill_match_ratio_text', '0/0')} ({skill_pct}%) | "
            f"AI Score {ai_score}/100 | Fit: {fit}"
        )

    chosen = st.selectbox(
        "Pick a shortlisted candidate to interview:",
        options=list(range(len(scored))),
        format_func=lambda idx: labels[idx],
    )
    cand_idx, cand = scored[chosen]

    interview = _get_or_init_interview_state(job, cand_idx)

    # Shortlist gate (optional)
    crit_score = int(cand["scoring"].get("skill_match_percent", 0))
    if crit_score < 60:
        st.warning(
            "This candidate is below the default shortlist threshold (Skill Matching Score < 60). "
            "You can still interview them, but consider shortlisting rules."
        )

    colA, colB = st.columns(2)
    with colA:
        if st.button("🧩 Generate Interview (6 questions)", key=f"gen_plan_{jid}_{cand_idx}"):
            plan = generate_interview_plan(
                jd_text=job["description"],
                jd_ai=job["ai_jd"],
                resume_text=cand["raw_text"],
                resume_ai=cand["ai"],
                scoring=cand["scoring"],
                n_questions=6,
            )
            interview["plan"] = plan
            interview["status"] = "ready"
            interview["q_index"] = 0
            interview["q_started_at"] = None
            interview["answers"] = []
            interview["final"] = None
            st.success("Interview generated. Click Start.")

    with colB:
        if st.button("🧹 Reset Interview", key=f"reset_{jid}_{cand_idx}"):
            cand["interview"] = {
                "status": "not_started",
                "plan": None,
                "q_index": 0,
                "q_started_at": None,
                "answers": [],
                "final": None,
            }
            st.success("Interview reset.")

    plan = interview.get("plan")
    if not plan:
        st.info("Generate an interview plan to begin.")
        return

    # Plan overview (optional)
    with st.expander("Interview Plan (overview)", expanded=False):
        st.json(
            {
                "title": plan.get("title"),
                "instructions": plan.get("instructions"),
                "questions": plan.get("questions", []),
            }
        )

    # Start interview
    if interview["status"] in ("ready", "not_started"):
        if st.button("▶️ Start Interview", key=f"start_{jid}_{cand_idx}"):
            interview["status"] = "in_progress"
            interview["q_index"] = 0
            interview["q_started_at"] = now_ts()
            st.success("Interview started.")

    # Completed view
    if interview["status"] == "completed":
        _render_completed_breakdown(interview, cand.get("name", "—"))
        return

    if interview["status"] != "in_progress":
        return

    questions = plan.get("questions", [])
    q_index = int(interview.get("q_index", 0))

    # If finished, finalize
    if q_index >= len(questions):
        final = compute_interview_score(interview.get("answers", []))
        interview["final"] = final
        interview["status"] = "completed"
        _render_completed_breakdown(interview, cand.get("name", "—"))
        return

    # Running score so far (based on submitted answers)
    if interview.get("answers"):
        running = compute_interview_score(interview.get("answers", []))
        avg_5 = running.get("average_0_to_5", None)
        score_100 = running.get("interview_score", None)
        if avg_5 is not None and score_100 is not None:
            st.info(f"Running score: {avg_5:.2f}/5  ({score_100:.1f}/100)")

    q = questions[q_index]
    time_limit = int(q.get("time_limit_sec", 120))

    # start timer if not started
    if interview.get("q_started_at") is None:
        interview["q_started_at"] = now_ts()

    elapsed = int(now_ts() - float(interview["q_started_at"]))
    remaining = max(0, time_limit - elapsed)
    timed_out = remaining <= 0

    st.write(f"## Question {q_index + 1} / {len(questions)}")
    st.write(
        f"**Skill:** {q.get('skill')}  |  **Difficulty:** {q.get('difficulty')}  |  **Time limit:** {time_limit}s"
    )
    st.write(f"⏱️ **Time remaining:** {remaining}s" + (" — **TIME UP**" if timed_out else ""))

    st.write("### Question")
    st.info(q.get("question", ""))

    # Show rubric / grading criteria before they answer
    _render_rubric(q.get("expected_points", []))

    # Candidate answer input
    answer_key = f"ans_{jid}_{cand_idx}_{q_index}"
    default_val = st.session_state.get(answer_key, "")
    answer = st.text_area("Your answer:", value=default_val, height=160, key=answer_key)

    # Buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        submit_clicked = st.button("✅ Submit Answer", key=f"submit_{jid}_{cand_idx}_{q_index}")

    with col2:
        if st.button("🔄 Refresh Timer", key=f"refresh_{jid}_{cand_idx}_{q_index}"):
            st.rerun()

    with col3:
        auto_next_clicked = False
        if timed_out:
            auto_next_clicked = st.button("⏭️ Time’s up — Next", key=f"timeout_next_{jid}_{cand_idx}_{q_index}")

    if submit_clicked or auto_next_clicked:
        final_answer = (answer or "").strip()
        final_elapsed = int(now_ts() - float(interview["q_started_at"]))
        final_timed_out = final_elapsed > time_limit

        eval_out = evaluate_answer(
            jd_text=job["description"],
            resume_text=cand["raw_text"],
            question_obj=q,
            answer_text=final_answer,
            timed_out=final_timed_out,
            time_taken_sec=final_elapsed,
        )

        # Store question text too (helps completed breakdown)
        interview["answers"].append(
            {
                "question_id": q.get("id", q_index + 1),
                "question_text": q.get("question", ""),
                "skill": q.get("skill"),
                "difficulty": q.get("difficulty"),
                "time_limit_sec": time_limit,
                "time_taken_sec": final_elapsed,
                "timed_out": final_timed_out,
                "answer_text": final_answer,
                **eval_out,
            }
        )

        interview["q_index"] = q_index + 1
        interview["q_started_at"] = now_ts()

        st.success(f"Saved Q{q_index + 1}. Score: {eval_out.get('score_0_to_5')}/5")
        _render_scorecard(eval_out)

        with st.expander("Debug: raw evaluation output", expanded=False):
            st.json(eval_out)

        st.rerun()

    # Progress + recent answers
    st.write("### Progress")
    st.write(f"Answered: {len(interview.get('answers', []))} / {len(questions)}")

    if interview.get("answers"):
        st.write("### Previous Answers (latest first)")
        for a in reversed(interview["answers"][-3:]):  # show last 3
            st.markdown(f"**Q{a.get('question_id')} — {a.get('skill')} | {a.get('score_0_to_5')}/5**")
            st.write(
                f"Time: {a.get('time_taken_sec')}s (limit {a.get('time_limit_sec')}s) | "
                f"Timed out: {a.get('timed_out')}"
            )
            fb = (a.get("feedback") or "").strip()
            if fb:
                st.write(fb)