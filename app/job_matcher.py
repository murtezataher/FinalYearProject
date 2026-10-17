"""
job_matcher.py – FINAL FIXED VERSION
Optimized for:
- WordPress job descriptions
- Multi-word skill phrases
- Accurate keyword + semantic matching
"""

import re
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util

embedder = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------------------------------------
# UPDATED SKILL LIST
# ---------------------------------------------------------

TECH_SKILLS = [
    # WordPress ecosystem
    "wordpress", "woocommerce", "elementor", "wpbakery",
    "advanced custom fields", "acf", "contact form 7",
    "themes", "plugins", "wordpress core",

    # Web Development
    "html", "css", "javascript", "php", "jquery",

    # SEO + Performance
    "seo", "on page seo", "technical seo",
    "performance optimization", "site speed", "caching",

    # Hosting / Deployment
    "cpanel", "dns", "ftp", "ssl",
    "apache", "nginx", "cloudflare", "hosting",

    # Bonus frameworks
    "react", "vue"
]

SOFT_SKILLS = [
    "communication", "problem solving", "time management",
    "attention to detail", "teamwork", "adaptability",
    "troubleshooting", "multitasking", "collaboration"
]

TOOLS = [
    "cloudflare", "cpanel", "ftp", "github", "gitlab", "bitbucket"
]


# ---------------------------------------------------------
# CLEAN + NORMALIZE JD TEXT
# ---------------------------------------------------------

def preprocess_jd(jd_text: str) -> str:
    jd = jd_text.lower()
    jd = jd.replace("\n", " ")
    jd = jd.replace("\r", " ")

    # normalize punctuation to spaces
    jd = re.sub(r"[^a-z0-9]+", " ", jd)

    jd = re.sub(r"\s+", " ", jd).strip()
    return jd


# ---------------------------------------------------------
# SKILL EXTRACTION
# ---------------------------------------------------------

def extract_skills_from_jd(jd_text: str) -> Dict[str, List[str]]:
    jd = preprocess_jd(jd_text)

    tech_found = []
    soft_found = []
    tool_found = []

    # Special: Multi-word phrases should match via substring
    # Single words via boundary
    def skill_matches(term):
        if " " in term:        # multi-word → substring match
            return term in jd
        else:                  # single-word → word boundary
            return re.search(rf"\b{re.escape(term)}\b", jd) is not None

    for s in TECH_SKILLS:
        if skill_matches(s):
            tech_found.append(s)

    for s in SOFT_SKILLS:
        if skill_matches(s):
            soft_found.append(s)

    for s in TOOLS:
        if skill_matches(s):
            tool_found.append(s)

    return {
        "tech": list(dict.fromkeys(tech_found)),
        "soft": list(dict.fromkeys(soft_found)),
        "tools": list(dict.fromkeys(tool_found)),
    }


# ---------------------------------------------------------
# KEYWORD OVERLAP
# ---------------------------------------------------------

def compute_keyword_overlap(jd_skills: Dict[str, List[str]], resume_skills: List[str]) -> float:
    jd_all = jd_skills["tech"] + jd_skills["soft"] + jd_skills["tools"]
    if not jd_all:
        return 0.0

    resume_set = set([s.lower() for s in resume_skills])

    match_count = sum(1 for skill in jd_all if skill.lower() in resume_set)

    return match_count / len(jd_all)


# ---------------------------------------------------------
# SEMANTIC SIMILARITY
# ---------------------------------------------------------

def compute_semantic_similarity(jd_text: str, resume_text: str) -> float:
    jd_emb = embedder.encode(jd_text, convert_to_tensor=True)
    res_emb = embedder.encode(resume_text, convert_to_tensor=True)
    return util.cos_sim(jd_emb, res_emb).item()


# ---------------------------------------------------------
# FINAL SKILL MATCH SCORE (0–100)
# ---------------------------------------------------------

def compute_skill_match_score(jd_text: str, resume_text: str, resume_skills: List[str]) -> float:

    jd_skills = extract_skills_from_jd(jd_text)

    kw = compute_keyword_overlap(jd_skills, resume_skills)
    sem = compute_semantic_similarity(jd_text, resume_text)

    final_score = (0.4 * kw) + (0.6 * sem)

    return round(final_score * 100, 2)
