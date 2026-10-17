# ai_jd_parser.py
# AI JD Parser WITH O*NET MAPPING + Full Skill Extraction

from openai import OpenAI
from openai_config import OPENAI_API_KEY
import json

client = OpenAI(api_key=OPENAI_API_KEY)


def ai_parse_jd(jd_text: str):

    if not jd_text:
        return {
            "role_title": "",
            "role_summary": "",
            "responsibilities": [],
            "required_tech_skills": [],
            "required_soft_skills": [],
            "tools": [],
            "experience_years_required": 0,
            "must_have": [],
            "nice_to_have": [],
            "seniority": "",
            "domains": [],
            "missing_common_skills": [],
            "onet_skill_categories": [],
            "onet_tools_categories": [],
            "onet_categories": [],
            "all_skills_extracted": [],
            "error": "Empty JD text",
        }

    # safety limit
    jd_text = jd_text[:2500]

    prompt = f"""
You are an advanced Job Description Skill Extraction Engine.

Your task is to EXTRACT EVERY SINGLE SKILL mentioned in the job description.

Extract skills in these categories:

1. Programming Languages (e.g. C#, Python)
2. Frameworks & Libraries (e.g. ASP.NET, .NET Core, React, Next.js)
3. Backend Technologies (e.g. Web API, REST APIs)
4. Frontend Technologies (e.g. JavaScript, React, Next.js)
5. Databases (e.g. MSSQL Server, query optimization, data modeling)
6. Cloud & DevOps (e.g. Azure, Azure DevOps, CI/CD, pipelines, deployment automation)
7. Tools & Platforms (e.g. Databricks, Git, Docker)
8. Methodologies (e.g. Agile, Scrum)
9. Leadership & Soft Skills (e.g. mentoring, collaboration, stakeholder engagement, communication)
10. Any other clearly identifiable technical or professional skills.

RULES:
- DO NOT summarize skills.
- DO NOT merge multiple skills into one string.
- Extract each individual skill as its own list item.
- Preserve important multi-word terms (e.g. "Azure DevOps", "MSSQL Server").

Field meaning:

- "required_tech_skills": core technical skills required for this role (languages, frameworks, databases, cloud, devops, tools).
- "required_soft_skills": leadership, communication, stakeholder engagement, mentoring, problem solving, etc.
- "tools": named tools / platforms / services (Azure DevOps, Databricks, Git, Jenkins, etc.).
- "all_skills_extracted": every unique skill from the JD (union of all of the above, no duplicates).
- "onet_skill_categories": O*NET skill categories for this JD (e.g. "Programming", "Systems Analysis", "Systems Evaluation").
- "onet_tools_categories": O*NET tools & technology categories (e.g. "Development software", "Database management system software").
- "onet_categories": a flat list of ALL O*NET categories used above (skills + tools + work activities).

Return ONLY JSON with EXACT structure:

{{
    "role_title": "",
    "role_summary": "",
    "responsibilities": [],
    "required_tech_skills": [],
    "required_soft_skills": [],
    "tools": [],
    "experience_years_required": 0,
    "must_have": [],
    "nice_to_have": [],
    "seniority": "",
    "domains": [],
    "missing_common_skills": [],
    "onet_skill_categories": [],
    "onet_tools_categories": [],
    "onet_categories": [],
    "all_skills_extracted": []
}}

Job Description:
\"\"\"{jd_text}\"\"\"
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )

        data = json.loads(res.choices[0].message.content)

        # Safe defaults with correct types
        data.setdefault("role_title", "")
        data.setdefault("role_summary", "")
        data.setdefault("responsibilities", [])
        data.setdefault("required_tech_skills", [])
        data.setdefault("required_soft_skills", [])
        data.setdefault("tools", [])
        data.setdefault("experience_years_required", 0)
        data.setdefault("must_have", [])
        data.setdefault("nice_to_have", [])
        data.setdefault("seniority", "")
        data.setdefault("domains", [])
        data.setdefault("missing_common_skills", [])
        data.setdefault("onet_skill_categories", [])
        data.setdefault("onet_tools_categories", [])
        data.setdefault("onet_categories", [])
        data.setdefault("all_skills_extracted", [])

        return data

    except Exception as e:
        return {
            "role_title": "",
            "role_summary": "",
            "responsibilities": [],
            "required_tech_skills": [],
            "required_soft_skills": [],
            "tools": [],
            "experience_years_required": 0,
            "must_have": [],
            "nice_to_have": [],
            "seniority": "",
            "domains": [],
            "missing_common_skills": [],
            "onet_skill_categories": [],
            "onet_tools_categories": [],
            "onet_categories": [],
            "all_skills_extracted": [],
            "error": f"AI JD parser failed: {str(e)}",
        }
