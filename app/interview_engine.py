# ================================================================
# interview_engine.py
# Timed per-question AI interview (Option B)
# - Generates interview questions tailored to JD + candidate gaps
# - Evaluates each answer with a rubric score (0–5)
# ================================================================

import json
import time
from typing import Dict, Any, List

from openai import OpenAI
from openai_config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def _safe_list(x):
    return x if isinstance(x, list) else []


def _difficulty_time_limit(difficulty: str) -> int:
    difficulty = (difficulty or "").lower().strip()
    if difficulty == "easy":
        return 60
    if difficulty == "hard":
        return 180
    return 120  # medium default


# ---------------------------------------------------------
# 1) GENERATE INTERVIEW PLAN
# ---------------------------------------------------------
def generate_interview_plan(
    jd_text: str,
    jd_ai: Dict[str, Any],
    resume_text: str,
    resume_ai: Dict[str, Any],
    scoring: Dict[str, Any],
    n_questions: int = 6,
) -> Dict[str, Any]:
    """
    Generates a tailored, non-repetitive interview plan:
    - 2 questions on claimed strengths (from resume)
    - 2 questions targeting gaps (missing_* from scoring)
    - 1 troubleshooting scenario
    - 1 communication/stakeholder question
    Enforces diversity: auto-regenerates if duplicates detected.
    """

    # -----------------------------
    # Helper: dedupe / normalize
    # -----------------------------
    def norm(s: str) -> str:
        return " ".join((s or "").lower().split())

    def has_too_many_duplicates(questions: List[Dict[str, Any]]) -> bool:
        texts = [norm(q.get("question", "")) for q in questions if isinstance(q, dict)]
        unique = len(set(texts))
        # require at least 80% unique
        return unique < max(1, int(0.8 * len(texts)))

    def enforce_time_limits(q: Dict[str, Any]) -> Dict[str, Any]:
        q.setdefault("skill", "General")
        q.setdefault("difficulty", "medium")
        q.setdefault("question", "")
        q.setdefault("expected_points", [])

        diff = (q.get("difficulty") or "medium").lower().strip()
        if diff not in ("easy", "medium", "hard"):
            diff = "medium"
        q["difficulty"] = diff

        tl = q.get("time_limit_sec")
        if not isinstance(tl, int) or tl <= 0:
            q["time_limit_sec"] = _difficulty_time_limit(diff)
        return q

    # -----------------------------
    # Build strong anchors
    # -----------------------------
    missing_tech = _safe_list(scoring.get("missing_tech"))
    missing_tools = _safe_list(scoring.get("missing_tools"))
    missing_soft = _safe_list(scoring.get("missing_soft"))

    required_tech = _safe_list(jd_ai.get("required_tech_skills"))
    required_soft = _safe_list(jd_ai.get("required_soft_skills"))
    jd_tools = _safe_list(jd_ai.get("tools"))

    candidate_tech = _safe_list(resume_ai.get("tech_skills"))
    candidate_tools = _safe_list(resume_ai.get("tools"))
    candidate_soft = _safe_list(resume_ai.get("soft_skills"))
    candidate_titles = _safe_list(resume_ai.get("job_titles"))

    # Use a short resume excerpt as evidence anchors (very helpful)
    resume_excerpt = (resume_text or "")[:1200]
    jd_excerpt = (jd_text or "")[:1200]

    # Prefer asking about: (a) claimed skills (b) gaps (c) core JD requirements
    claimed_focus = (candidate_tech + candidate_tools)[:20]
    gap_focus = (missing_tech + missing_tools + missing_soft)[:20]
    jd_focus = (required_tech + jd_tools + required_soft)[:25]

    # -----------------------------
    # Regeneration loop (diversity guard)
    # -----------------------------
    max_attempts = 3
    last_data = None

    for attempt in range(1, max_attempts + 1):
        prompt = f"""
You are an expert hiring manager and technical interviewer.

Create a CUSTOM interview for THIS candidate applying to THIS job.

You MUST generate {n_questions} DISTINCT questions (no duplicates).
Each question must be tied to one of these:
- the job requirements (JD focus)
- the candidate's resume claims (claimed focus)
- the candidate's skill gaps from screening (gap focus)

Distribution requirements (all must be satisfied):
- 2 questions to verify resume claims (use resume excerpt evidence)
- 2 questions targeting gaps / missing skills (from gap focus)
- 1 troubleshooting/debugging scenario relevant to the stack
- 1 communication/stakeholder or requirement-clarification question

Question writing rules:
- Every question must reference a specific skill/tool/domain from the focus lists.
- Do NOT repeat the same skill focus more than once unless it’s a follow-up.
- Make questions practical, like real work situations.
- Each question includes expected_points (3–6) describing what a strong answer covers.

Time limits:
- easy=60 sec, medium=120 sec, hard=180 sec.

Return ONLY JSON (no markdown) with EXACT structure:

{{
  "title": "",
  "instructions": "",
  "questions": [
    {{
      "id": 1,
      "skill": "",
      "difficulty": "easy|medium|hard",
      "time_limit_sec": 120,
      "question": "",
      "expected_points": ["", ""]
    }}
  ]
}}

JOB DESCRIPTION (excerpt):
\"\"\"{jd_excerpt}\"\"\"

CANDIDATE RESUME (excerpt):
\"\"\"{resume_excerpt}\"\"\"

Candidate job titles (most recent first):
{candidate_titles[:6]}

JD focus (use these to ground questions):
{jd_focus}

Candidate claimed focus (verify these):
{claimed_focus}

Gap focus (probe these):
{gap_focus}

Extra constraints:
- Questions must be different from each other in wording AND topic.
- Do not output generic "tell me about yourself" questions.
"""

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads(res.choices[0].message.content)
        last_data = data

        data.setdefault("title", "Shortlisted Candidate Interview")
        data.setdefault("instructions", "Answer each question within the time limit.")
        questions = _safe_list(data.get("questions"))

        # Normalize
        cleaned = []
        for i, q in enumerate(questions, start=1):
            if not isinstance(q, dict):
                continue
            q["id"] = i
            cleaned.append(enforce_time_limits(q))

        # Trim/pad
        cleaned = cleaned[:n_questions]
        while len(cleaned) < n_questions:
            idx = len(cleaned) + 1
            cleaned.append({
                "id": idx,
                "skill": "Project Scoping",
                "difficulty": "medium",
                "time_limit_sec": 120,
                "question": "Given this job’s requirements, walk me through how you would plan and deliver your first 2 weeks on the project.",
                "expected_points": ["clarify requirements", "identify risks", "define milestones", "communicate with stakeholders"],
            })

        data["questions"] = cleaned

        # Diversity check
        if not has_too_many_duplicates(cleaned):
            return data

    # If all attempts still repetitive, return the last one (but it's better than crashing)
    return last_data or {
        "title": "Shortlisted Candidate Interview",
        "instructions": "Answer each question within the time limit.",
        "questions": [
            {
                "id": 1,
                "skill": "General",
                "difficulty": "medium",
                "time_limit_sec": 120,
                "question": "Describe a relevant project you worked on and what you delivered.",
                "expected_points": ["context", "your role", "stack", "impact"],
            }
        ],
    }


# ---------------------------------------------------------
# 2) EVALUATE ANSWER
# ---------------------------------------------------------
def evaluate_answer(
    jd_text: str,
    resume_text: str,
    question_obj: Dict[str, Any],
    answer_text: str,
    timed_out: bool,
    time_taken_sec: int,
) -> Dict[str, Any]:
    """
    Returns JSON:
    {
      "score_0_to_5": 0..5,
      "feedback": "...",
      "covered_points": [...],
      "missing_points": [...],
      "time_penalty_applied": true/false
    }
    """
    q = question_obj.get("question", "")
    expected = _safe_list(question_obj.get("expected_points"))
    difficulty = question_obj.get("difficulty", "medium")
    time_limit = int(question_obj.get("time_limit_sec", 120))

    prompt = f"""
You are an AI interview grader.

Grade the candidate's answer on a 0–5 scale using the expected_points as the rubric.
Also provide concise feedback and which expected points were covered/missed.

Rules:
- Return ONLY JSON.
- score_0_to_5 must be an integer 0..5.
- Be strict for vague answers.
- If timed_out is true, apply a penalty: cap score at 2 unless the answer is exceptionally complete.

Context:
difficulty={difficulty}
time_limit_sec={time_limit}
time_taken_sec={time_taken_sec}
timed_out={timed_out}

Question:
\"\"\"{q}\"\"\"

Expected points:
{json.dumps(expected)}

Candidate answer:
\"\"\"{(answer_text or "").strip()[:1800]}\"\"\"

Return JSON exactly:
{{
  "score_0_to_5": 0,
  "feedback": "",
  "covered_points": [],
  "missing_points": [],
  "time_penalty_applied": false
}}
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )

    out = json.loads(res.choices[0].message.content)

    # Normalize / enforce constraints
    score = out.get("score_0_to_5", 0)
    if not isinstance(score, int):
        try:
            score = int(score)
        except Exception:
            score = 0
    score = max(0, min(5, score))

    time_penalty = False
    if timed_out and score > 2:
        score = 2
        time_penalty = True

    out["score_0_to_5"] = score
    out.setdefault("feedback", "")
    out.setdefault("covered_points", [])
    out.setdefault("missing_points", [])
    out["time_penalty_applied"] = bool(out.get("time_penalty_applied")) or time_penalty

    return out


# ---------------------------------------------------------
# 3) FINAL INTERVIEW SCORE
# ---------------------------------------------------------
def compute_interview_score(answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Converts per-question 0..5 into 0..100.
    """
    if not answers:
        return {"interview_score": 0, "avg_score_0_to_5": 0.0}

    scores = []
    for a in answers:
        s = a.get("score_0_to_5", 0)
        if isinstance(s, int):
            scores.append(max(0, min(5, s)))

    avg = sum(scores) / max(1, len(scores))
    interview_score = round((avg / 5.0) * 100)

    return {"interview_score": interview_score, "avg_score_0_to_5": round(avg, 2)}


def now_ts() -> float:
    return time.time()