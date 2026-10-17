# ai_resume_parser.py
# AI Resume Parser WITH O*NET SKILL MAPPING (simplified, flat categories)

from openai import OpenAI
from openai_config import OPENAI_API_KEY
import json

client = OpenAI(api_key=OPENAI_API_KEY)


def ai_parse_resume(raw_text: str):

    if not raw_text:
        return {
            "tech_skills": [],
            "soft_skills": [],
            "tools": [],
            "job_titles": [],
            "experience_years": 0,
            "summary": "",
            "education": "",
            "missing_skills": [],
            "onet_categories": [],
            "error": "Empty resume text"
        }

    raw_text = raw_text[:3000]

    prompt = f"""
You are an AI Resume Parsing Engine.

1) Extract normal structured data from the resume.
2) Classify skills into O*NET skill clusters.

Field meaning:

- "tech_skills": programming languages, frameworks, databases, cloud, devops, data tools.
- "soft_skills": communication, leadership, teamwork, mentoring, problem-solving, etc.
- "tools": concrete tools / platforms (Azure DevOps, Git, Databricks, Docker, Jenkins, etc.).
- "job_titles": ordered list of job titles from most recent to oldest.
- "experience_years": total professional experience in years (integer).
- "summary": 2–4 sentence professional summary.
- "education": highest degree or main education line.
- "missing_skills": IMPORTANT skills that are commonly expected for similar profiles but NOT clearly present in the resume.
- "onet_categories": FLAT LIST of O*NET categories (strings) that apply to this candidate, e.g.:
    - "Programming"
    - "Systems Analysis"
    - "Systems Evaluation"
    - "Complex Problem Solving"
    - "Critical Thinking"
    - "Judging the Qualities of Objects, Services, or People"
    - "Development software"
    - "Database management system software"
    - "Attention to Detail"
    - "Leadership"

Return ONLY JSON with EXACT structure:

{{
  "tech_skills": [],
  "soft_skills": [],
  "tools": [],
  "job_titles": [],
  "experience_years": 0,
  "summary": "",
  "education": "",
  "missing_skills": [],
  "onet_categories": []
}}

Resume:
\"\"\"{raw_text}\"\"\"
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )

        data = json.loads(res.choices[0].message.content)

        # Safe defaults
        data.setdefault("tech_skills", [])
        data.setdefault("soft_skills", [])
        data.setdefault("tools", [])
        data.setdefault("job_titles", [])
        data.setdefault("experience_years", 0)
        data.setdefault("summary", "")
        data.setdefault("education", "")
        data.setdefault("missing_skills", [])
        data.setdefault("onet_categories", [])

        return data

    except Exception as e:
        return {
            "tech_skills": [],
            "soft_skills": [],
            "tools": [],
            "job_titles": [],
            "experience_years": 0,
            "summary": "",
            "education": "",
            "missing_skills": [],
            "onet_categories": [],
            "error": f"AI resume parser failed: {str(e)}",
        }
