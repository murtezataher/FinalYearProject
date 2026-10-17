# ================================================================
# video_interview.py  — Questions only, no scoring/marks
# ================================================================

import re
import streamlit as st
import streamlit.components.v1 as components

from interview_engine import generate_interview_plan, now_ts


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:30]


def _make_room_url(job_title: str, candidate_name: str, jid: str) -> str:
    slug = f"hirelens-{_slugify(job_title)}-{_slugify(candidate_name)}-{jid[-4:]}"
    return f"https://meet.jit.si/{slug}"


def _get_or_init_video_state(job: dict, cand_idx: int) -> dict:
    cand = job["candidates"][cand_idx]
    if "video_interview" not in cand or not isinstance(cand["video_interview"], dict):
        cand["video_interview"] = {
            "status": "not_started",
            "plan": None,
            "q_index": 0,
            "room_url": None,
        }
    return cand["video_interview"]


def _safe_list(x):
    return x if isinstance(x, list) else []


def _render_question_panel(q: dict, q_index: int, total: int):
    skill = q.get("skill", "")
    difficulty = q.get("difficulty", "medium")

    st.markdown(f"**Question {q_index + 1} of {total}**")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            f"<div class='kpi'><div class='label'>Skill</div>"
            f"<div class='value' style='font-size:14px'>{skill}</div></div>",
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            f"<div class='kpi'><div class='label'>Difficulty</div>"
            f"<div class='value' style='font-size:14px'>{difficulty.capitalize()}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.markdown("### Question")
    st.info(q.get("question", ""))

    points = _safe_list(q.get("expected_points", []))
    if points:
        with st.expander("Key points to listen for", expanded=True):
            for p in points:
                st.write("•", p)


def _render_completed(interview: dict, candidate_name: str):
    st.success("Video interview completed!")
    st.caption(f"Candidate: {candidate_name}")

    plan = interview.get("plan") or {}
    questions = _safe_list(plan.get("questions", []))
    total = len(questions)
    answered = interview.get("q_index", total)
    st.metric("Questions covered", f"{min(answered, total)} / {total}")

    with st.expander("Review all interview questions", expanded=False):
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1} — {q.get('skill', '')} ({q.get('difficulty','').capitalize()})**")
            st.write(q.get("question", "—"))
            for p in _safe_list(q.get("expected_points", [])):
                st.write("  •", p)
            st.markdown("---")


def render_video_interview_tab(job: dict, jid: str):
    st.subheader("Video Interview")

    if not job:
        st.info("Select a role first.")
        return
    if not job.get("ai_jd"):
        st.warning("Analyze the role first (Roles tab).")
        return
    if not job.get("candidates"):
        st.info("Add candidates first (Candidates tab).")
        return

    scored = [(i, c) for i, c in enumerate(job["candidates"]) if c.get("scoring")]
    if not scored:
        st.info("Compute scores first (Ranking tab).")
        return

    labels = []
    for i, c in scored:
        sc = c["scoring"]
        skill_pct = sc.get("skill_match_percent", 0)
        ai_score = sc.get("ai_semantic_score", 0)
        fit = sc.get("fit_label") or (
            "Strong" if ai_score >= 80 else "Moderate" if ai_score >= 50 else "Weak"
        )
        labels.append(
            f"{c['name']}  |  Skill {sc.get('skill_match_ratio_text','0/0')} ({skill_pct}%)  |  AI Score {ai_score}/100  |  Fit: {fit}"
        )

    chosen = st.selectbox(
        "Select candidate to interview:",
        options=list(range(len(scored))),
        format_func=lambda idx: labels[idx],
    )
    cand_idx, cand = scored[chosen]
    interview = _get_or_init_video_state(job, cand_idx)

    # ── NOT STARTED ──────────────────────────────────────────────
    if interview["status"] == "not_started":
        st.markdown("### Set up the video interview")
        st.write(
            "Generates a private Jitsi video room and 6 tailored interview "
            "questions for this candidate. Share the room link with the candidate."
        )
        if st.button("Generate interview plan", key=f"vid_gen_{jid}_{cand_idx}"):
            with st.spinner("Generating interview questions..."):
                plan = generate_interview_plan(
                    jd_text=job["description"],
                    jd_ai=job["ai_jd"],
                    resume_text=cand["raw_text"],
                    resume_ai=cand["ai"],
                    scoring=cand["scoring"],
                    n_questions=6,
                )
            room_url = _make_room_url(job["title"], cand["name"], jid)
            interview["plan"] = plan
            interview["room_url"] = room_url
            interview["status"] = "in_call"
            interview["q_index"] = 0
            st.success("Questions ready. Room link generated.")
            st.rerun()
        return

    # ── COMPLETED ────────────────────────────────────────────────
    if interview["status"] == "completed":
        _render_completed(interview, cand.get("name", "—"))
        if st.button("Reset interview", key=f"vid_reset_done_{jid}_{cand_idx}"):
            cand["video_interview"] = {}
            st.rerun()
        return

    # ── IN CALL ──────────────────────────────────────────────────
    plan = interview.get("plan")
    if not plan:
        st.error("No interview plan found. Please reset and regenerate.")
        return

    questions = _safe_list(plan.get("questions", []))
    q_index = int(interview.get("q_index", 0))

    if q_index >= len(questions):
        interview["status"] = "completed"
        _render_completed(interview, cand.get("name", "—"))
        return

    q = questions[q_index]
    room_url = interview.get("room_url", "")

    st.caption(f"Progress: {q_index} / {len(questions)} questions")
    st.progress(q_index / len(questions))

    # Room link
    copy_html = f"""
    <div class='card' style='display:flex;align-items:center;gap:12px;flex-wrap:wrap;'>
        <span class='muted' style='white-space:nowrap;'>Room link:</span>
        <code style='flex:1;word-break:break-all;min-width:200px;'>{room_url}</code>
        <button onclick="navigator.clipboard.writeText('{room_url}').then(()=>{{this.textContent='Copied!';setTimeout(()=>this.textContent='Copy link',1800)}})"
            style='padding:6px 14px;border-radius:8px;border:1px solid #3b82f6;background:#1e3a5f;
                   color:#93c5fd;font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap;'>
            Copy link
        </button>
    </div>
    """
    st.markdown(copy_html, unsafe_allow_html=True)
    st.caption("Share this link with the candidate. No account needed.")
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    # Video left | Question right
    vid_col, q_col = st.columns([1.1, 1])

    with vid_col:
        st.markdown("### Video call")
        components.html(
            f'<iframe src="{room_url}" allow="camera; microphone; fullscreen; display-capture; autoplay" '
            f'style="width:100%; height:520px; border:none; border-radius:12px;"></iframe>',
            height=540, scrolling=False
        )

    with q_col:
        _render_question_panel(q, q_index, len(questions))
        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            label = "Next question →" if q_index < len(questions) - 1 else "Finish interview"
            if st.button(label, key=f"vid_next_{jid}_{cand_idx}_{q_index}", use_container_width=True):
                interview["q_index"] = q_index + 1
                if interview["q_index"] >= len(questions):
                    interview["status"] = "completed"
                st.rerun()
        with btn_col2:
            if st.button("Skip question", key=f"vid_skip_{jid}_{cand_idx}_{q_index}", use_container_width=True):
                interview["q_index"] = q_index + 1
                if interview["q_index"] >= len(questions):
                    interview["status"] = "completed"
                st.rerun()

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    if st.button("Reset video interview", key=f"vid_reset_{jid}_{cand_idx}"):
        cand["video_interview"] = {}
        st.rerun()