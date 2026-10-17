# ================================================================
#  ranking_engine.py
#  Criteria Scoring + O*NET Scoring + AI Semantic Scoring
# ================================================================

import json
from openai import OpenAI
from openai_config import OPENAI_API_KEY  # <-- FIXED import

client = OpenAI(api_key=OPENAI_API_KEY)


# ================================================================
# 1) CRITERIA-BASED (RULE BASED) SCORE
# ================================================================
def criteria_based_score(jd_ai, resume_ai):
    """
    Returns:
    - skill_match_percent (0-100)
    - skill_match_ratio_text e.g. "12/23"
    - matched + missing lists (tech/tools/soft)
    """

    # JD soft skills
    jd_soft = set(
        s.lower() for s in (jd_ai.get("required_soft_skills", []) or [])
        if isinstance(s, str)
    )

    # JD technical skills
    jd_all_skills = set(
        s.lower() for s in (jd_ai.get("all_skills_extracted", []) or [])
        if isinstance(s, str)
    )
    jd_required_tech = set(
        s.lower() for s in (jd_ai.get("required_tech_skills", []) or [])
        if isinstance(s, str)
    )
    jd_tech = (jd_all_skills | jd_required_tech) - jd_soft

    # JD tools
    jd_tools = set(
        t.lower() for t in (jd_ai.get("tools", []) or [])
        if isinstance(t, str)
    )

    # CV skills
    cv_tech = set(
        s.lower()
        for s in (resume_ai.get("tech_skills", []) or []) + (resume_ai.get("tools", []) or [])
        if isinstance(s, str)
    )
    cv_tools = set(
        t.lower() for t in (resume_ai.get("tools", []) or [])
        if isinstance(t, str)
    )
    cv_soft = set(
        s.lower() for s in (resume_ai.get("soft_skills", []) or [])
        if isinstance(s, str)
    )

    # Matches
    matched_tech = sorted(jd_tech & cv_tech)
    missing_tech = sorted(jd_tech - cv_tech)

    matched_tools = sorted(jd_tools & cv_tools)
    missing_tools = sorted(jd_tools - cv_tools)

    matched_soft = sorted(jd_soft & cv_soft)
    missing_soft = sorted(jd_soft - cv_soft)

    # Totals (for ratio)
    total_required = len(jd_tech) + len(jd_tools) + len(jd_soft)
    total_matched = len(matched_tech) + len(matched_tools) + len(matched_soft)

    skill_match_percent = round((total_matched / total_required) * 100) if total_required else 0
    skill_match_ratio_text = f"{total_matched}/{total_required}" if total_required else "0/0"

    return {
        "skill_match_percent": skill_match_percent,
        "skill_match_ratio_text": skill_match_ratio_text,
        "skill_match_matched": total_matched,
        "skill_match_total": total_required,

        "matched_tech": matched_tech,
        "missing_tech": missing_tech,
        "matched_tools": matched_tools,
        "missing_tools": missing_tools,
        "matched_soft": matched_soft,
        "missing_soft": missing_soft,
    }



# ================================================================
# 3) AI SEMANTIC SCORE (GPT-4o-mini)
# ================================================================
def ai_semantic_score(jd_text, resume_text):
    """GPT generates a meaning-based match score (0-100)."""

    prompt = f"""
You are an AI hiring engine.

Read the Job Description and Resume, and give a match score based on meaning,
not keyword matching.

Return JSON ONLY with "ai_semantic_score" as an INTEGER from 0 to 100:

{{
  "ai_semantic_score": 0,
  "fit": "",
  "reason": ""
}}

JD:
\"\"\"{jd_text[:2000]}\"\"\"

RESUME:
\"\"\"{resume_text[:2000]}\"\"\"
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )

        data = json.loads(res.choices[0].message.content)

        # Normalize score to int 0-100 (handle float + 0-1 scale)
        raw = data.get("ai_semantic_score", 0)
        try:
            raw = float(raw)
        except Exception:
            raw = 0.0

        if 0.0 <= raw <= 1.0:
            raw = raw * 100.0

        score = int(round(raw))
        score = max(0, min(100, score))
        data["ai_semantic_score"] = score

        # Fit label (optional – not used as recommendation)
        if not data.get("fit"):
            if score >= 80:
                data["fit"] = "Strong"
            elif score >= 50:
                data["fit"] = "Moderate"
            else:
                data["fit"] = "Weak"

        data.setdefault("reason", "")

        return data

    except Exception as e:
        return {
            "ai_semantic_score": 0,
            "fit": "Error",
            "reason": f"AI scoring failed: {str(e)}",
        }


# ================================================================
# 4) AI EXPLANATION (Evidence-based reasoning)
# ================================================================
def generate_ai_explanation(jd_text, resume_text, scoring_data):
    """
    Evidence-based reasoning:
    - Why the resume matches / doesn't match the JD
    - Concrete evidence snippets from the resume
    - Clear gaps + improvement suggestions
    """

    prompt = f"""
You are an AI hiring analyst. Your job is to EXPLAIN why a resume matches a job.

You MUST:
- Use concrete evidence from the RESUME (short quotes or snippets).
- Reference JD requirements.
- Be specific and non-generic.
- If evidence is missing, say "No clear evidence found".

Return JSON ONLY in this exact structure:

{{
  "ai_reasoning_summary": "",
  "evidence_matches": [
    {{
      "requirement": "",
      "evidence_from_resume": "",
      "confidence": "High|Medium|Low"
    }}
  ],
  "evidence_gaps": [
    {{
      "missing_requirement": "",
      "why_it_matters": ""
    }}
  ],
  "suggested_improvements": [
    "..."
  ]
}}

SCORING DATA (context):
{json.dumps(scoring_data, ensure_ascii=False)}

JOB DESCRIPTION:
\"\"\"{jd_text[:2200]}\"\"\"

RESUME:
\"\"\"{resume_text[:2200]}\"\"\"
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads(res.choices[0].message.content)

        data.setdefault("ai_reasoning_summary", "")
        data.setdefault("evidence_matches", [])
        data.setdefault("evidence_gaps", [])
        data.setdefault("suggested_improvements", [])

        data["evidence_matches"] = (data["evidence_matches"] or [])[:6]
        data["evidence_gaps"] = (data["evidence_gaps"] or [])[:6]
        data["suggested_improvements"] = (data["suggested_improvements"] or [])[:6]

        return data

    except Exception as e:
        return {
            "ai_reasoning_summary": f"AI reasoning error: {str(e)}",
            "evidence_matches": [],
            "evidence_gaps": [],
            "suggested_improvements": [],
        }


# ================================================================
# 5) EXPERIENCE SCORE (0-100)
# ================================================================
def experience_score(jd_ai, resume_ai):
    """
    Compares candidate experience years vs JD required years.
    - Meets or exceeds requirement → 100
    - Under by 1 yr → 75, 2 yrs → 50, 3+ yrs → 25
    - No requirement in JD → neutral 70 (don't penalise)
    """
    required = jd_ai.get("experience_years_required") or 0
    candidate = resume_ai.get("experience_years") or 0

    try:
        required = int(required)
        candidate = int(candidate)
    except Exception:
        return 70  # neutral fallback

    if required == 0:
        return 70  # JD didn't specify — neutral

    if candidate >= required:
        return 100

    gap = required - candidate
    if gap == 1:
        return 75
    if gap == 2:
        return 50
    return 25


# ================================================================
# 7) FINAL WEIGHTED SCORE
# ================================================================
def compute_final_score(skill_pct, semantic_score, exp_score):
    """
    Weighted formula:
      42.5% skill match (keyword)
      42.5% AI semantic score
      15%   experience score
    """
    raw = (
        0.425 * skill_pct +
        0.425 * semantic_score +
        0.15  * exp_score
    )
    return round(max(0, min(100, raw)))


# ================================================================
# 8) MAIN FUNCTION — COMBINE ALL SCORES
# ================================================================
def ai_score_candidate(jd_text, jd_ai, resume_text, resume_ai):
    # Skill matching breakdown (ratio + lists)
    skill = criteria_based_score(jd_ai, resume_ai)

    # AI semantic score
    ai_smart = ai_semantic_score(jd_text, resume_text)

    # Experience score
    exp = experience_score(jd_ai, resume_ai)

    # Final weighted score
    final = compute_final_score(
        skill_pct=skill["skill_match_percent"],
        semantic_score=ai_smart.get("ai_semantic_score", 0),
        exp_score=exp,
    )

    # Fit label based on final score
    if final >= 80:
        fit_label = "Strong"
    elif final >= 60:
        fit_label = "Good"
    elif final >= 40:
        fit_label = "Moderate"
    else:
        fit_label = "Weak"

    # AI reasoning (evidence)
    explanation = generate_ai_explanation(
        jd_text,
        resume_text,
        {
            "skill_match_percent": skill["skill_match_percent"],
            "skill_match_ratio_text": skill["skill_match_ratio_text"],
            "ai_semantic_score": ai_smart["ai_semantic_score"],
            "experience_score": exp,
            "final_score": final,
        }
    )

    return {
        # ── FINAL SCORE ──
        "final_score": final,
        "fit_label": fit_label,

        # ── SCORE BREAKDOWN ──
        "skill_match_percent": skill["skill_match_percent"],
        "skill_match_ratio_text": skill["skill_match_ratio_text"],
        "skill_match_matched": skill["skill_match_matched"],
        "skill_match_total": skill["skill_match_total"],
        "ai_semantic_score": ai_smart.get("ai_semantic_score", 0),
        "ai_semantic_fit": ai_smart.get("fit", ""),
        "ai_semantic_reason": ai_smart.get("reason", ""),
        "experience_score": exp,

        # ── MATCHED vs MISSING LISTS ──
        "matched_tech": skill["matched_tech"],
        "missing_tech": skill["missing_tech"],
        "matched_tools": skill["matched_tools"],
        "missing_tools": skill["missing_tools"],
        "matched_soft": skill["matched_soft"],
        "missing_soft": skill["missing_soft"],

        # ── EVIDENCE-BASED REASONING ──
        "ai_reasoning_summary": explanation.get("ai_reasoning_summary", ""),
        "evidence_matches": explanation.get("evidence_matches", []),
        "evidence_gaps": explanation.get("evidence_gaps", []),
        "suggested_improvements": explanation.get("suggested_improvements", []),
    }