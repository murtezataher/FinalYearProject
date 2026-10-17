"""
resume_parser.py – UPDATED VERSION
Includes:
- WordPress ecosystem skill extraction
- PHP, Hosting, SEO detection
- Improved skill normalization
- Enhanced extraction accuracy
"""

import os
import re
from typing import Dict, Any, List

import fitz
import pdfplumber
import pytesseract
from PIL import Image

from huggingface_extractor import HF_NER_SkillExtractor

hf_ner = HF_NER_SkillExtractor()

try:
    from sentence_transformers import SentenceTransformer, util
    SEM_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
except Exception:
    SEM_MODEL = None


# ---------------------------------------------------------
# TESSERACT PATH
# ---------------------------------------------------------
_POSSIBLE_TESS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    rf"C:\Users\{os.getlogin()}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]

for _p in _POSSIBLE_TESS:
    if os.path.exists(_p):
        pytesseract.pytesseract.tesseract_cmd = _p
        break


# ---------------------------------------------------------
# TEXT CLEANING
# ---------------------------------------------------------
def clean_text(text: str) -> str:
    text = text.replace("\r", " ").replace("\t", " ")
    text = re.sub(r"\n{2,}", "\n", text)
    return re.sub(r" +", " ", text).strip()


# ---------------------------------------------------------
# FILE TYPE HELPERS
# ---------------------------------------------------------
def is_pdf(path: str) -> bool:
    return path.lower().endswith(".pdf")

def is_docx(path: str) -> bool:
    return path.lower().endswith(".docx")

def is_image(path: str) -> bool:
    return any(path.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png"))


# ---------------------------------------------------------
# TEXT EXTRACTION (PDF / DOCX / IMAGE)
# ---------------------------------------------------------
def extract_text_from_pdf(path: str) -> str:
    text = ""
    doc = fitz.open(path)
    for page in doc:
        part = page.get_text()
        if part:
            text += part

    if len(text.strip()) < 50:  # scanned
        ocr_text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                img = Image.fromarray(page.to_image(resolution=300).original)
                try:
                    ocr_text += pytesseract.image_to_string(img)
                except:
                    pass
        text = ocr_text

    return clean_text(text)


def extract_text_from_docx(path: str) -> str:
    from docx import Document
    doc = Document(path)
    return clean_text("\n".join(p.text for p in doc.paragraphs if p.text.strip()))


def extract_text_from_image(path: str) -> str:
    try:
        return clean_text(pytesseract.image_to_string(Image.open(path)))
    except:
        return ""


def extract_text(path: str) -> str:
    if is_pdf(path):
        return extract_text_from_pdf(path)
    if is_docx(path):
        return extract_text_from_docx(path)
    if is_image(path):
        return extract_text_from_image(path)
    raise ValueError("Unsupported file type.")


# ---------------------------------------------------------
# SECTION DETECTION
# ---------------------------------------------------------
SECTION_HEADERS = {
    "education": ["education", "academic", "academics", "studies"],
    "experience": ["experience", "work experience", "employment"],
    "skills": ["skills", "technical skills", "core skills"],
    "projects": ["projects"],
    "achievements": ["achievements", "awards", "honors"],
}

def detect_sections(text: str) -> Dict[str, str]:
    sections = {k: "" for k in SECTION_HEADERS}
    current = None

    for raw_line in text.split("\n"):
        line = raw_line.strip().lower()
        if not line:
            continue

        header_found = False

        for sec, keys in SECTION_HEADERS.items():
            for key in keys:
                if key in line:
                    current = sec
                    header_found = True
                    break
            if header_found:
                break

        if not header_found and current:
            sections[current] += raw_line.strip() + "\n"

    return sections


# ---------------------------------------------------------
# CONTACT INFO
# ---------------------------------------------------------
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}"
PHONE_REGEX = r"(\+?\d[\d \-\(\)]{8,}\d)"

def extract_contact(text: str) -> Dict[str, Any]:
    emails = list(dict.fromkeys(re.findall(EMAIL_REGEX, text)))

    raw_phones = re.findall(PHONE_REGEX, text)
    phones = []
    for ph in raw_phones:
        digits = re.sub(r"\D", "", ph)
        if len(digits) >= 10:
            phones.append(ph)
    phones = list(dict.fromkeys(phones))

    header_text = text[:400]
    names = hf_ner.extract_names(header_text)
    name = names[0] if names else None

    return {"name": name, "emails": emails, "phones": phones}


# ---------------------------------------------------------
# EDUCATION EXTRACTION
# ---------------------------------------------------------
DEGREE_KEYWORDS = [
    "bachelor", "bs", "bsc", "ba",
    "master", "ms", "msc", "ma",
    "mphil", "phd", "diploma",
]

def extract_education_entries(section_text: str) -> List[Dict[str, Any]]:
    results = []
    lines = [ln.strip() for ln in section_text.split("\n") if ln.strip()]

    for ln in lines:
        degree_found = any(d in ln.lower() for d in DEGREE_KEYWORDS)
        if degree_found:
            results.append({"raw_line": ln})
    return results


# ---------------------------------------------------------
# EXPERIENCE (BOUND TO EXPERIENCE SECTION)
# ---------------------------------------------------------
def extract_experience_entries(section_text: str) -> List[Dict[str, Any]]:
    entries = []
    lines = [ln.strip() for ln in section_text.split("\n") if ln.strip()]

    YEAR = r"(19\d{2}|20\d{2})"
    RANGE = r"(19\d{2}|20\d{2})\s*[-–to]+\s*(19\d{2}|20\d{2}|present)"

    for ln in lines:
        if re.search(YEAR, ln.lower()):
            entries.append({"raw": ln})
    return entries

def format_experience_lines(entries: List[Dict[str, Any]]) -> List[str]:
    return [e["raw"] for e in entries]


# ---------------------------------------------------------
# UPDATED SKILL DB (WORDPRESS + WEB DEV + SEO + HOSTING)
# ---------------------------------------------------------
SKILL_DB = {
    # WordPress Ecosystem
    "wordpress": ["wordpress", "wp"],
    "elementor": ["elementor"],
    "wpbakery": ["wpbakery", "wp bakery"],
    "woocommerce": ["woocommerce"],
    "acf": ["acf", "advanced custom fields"],
    "themes": ["themes", "theme development"],
    "plugins": ["plugins", "plugin development"],

    # Core Web
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "php": ["php"],
    "javascript": ["javascript", "js"],
    "jquery": ["jquery"],

    # SEO & Performance
    "seo": ["seo", "search engine optimization"],
    "performance optimization": ["performance optimization", "speed optimization", "site speed"],
    "caching": ["cache", "caching", "wpsupercache", "wp super cache"],

    # Hosting / DevOps
    "cpanel": ["cpanel"],
    "dns": ["dns"],
    "cloudflare": ["cloudflare"],
    "apache": ["apache"],
    "nginx": ["nginx"],
    "ftp": ["ftp"],
}

SKILL_SYNONYMS = {alias.lower(): canon for canon, aliases in SKILL_DB.items() for alias in aliases}


# ---------------------------------------------------------
# SKILL EXTRACTION
# ---------------------------------------------------------
def extract_skills_from_section(section_text: str) -> List[str]:
    tokens = []
    for ln in section_text.split("\n"):
        ln = ln.strip().lower()
        if not ln:
            continue
        ln = re.sub(r"^[•\-\*]+", "", ln).strip()

        parts = re.split(r"[,/|]", ln)
        for p in parts:
            p = p.strip().lower()
            if p:
                tokens.append(p)
    return tokens


def keyword_skill_extractor(full_text: str) -> List[str]:
    found = []
    t = full_text.lower()
    for canon, aliases in SKILL_DB.items():
        for a in aliases:
            if a.lower() in t:
                found.append(canon)
    return list(dict.fromkeys(found))


def semantic_skill_enrichment(full_text: str, skills: List[str]) -> List[str]:
    if SEM_MODEL is None:
        return skills

    try:
        lines = [ln for ln in full_text.split("\n") if len(ln.split()) >= 2]
        if not lines:
            return skills

        canonical = list(SKILL_DB.keys())
        emb_lines = SEM_MODEL.encode(lines, convert_to_tensor=True)
        emb_ref = SEM_MODEL.encode(canonical, convert_to_tensor=True)

        sim = util.cos_sim(emb_lines, emb_ref)

        enriched = set(skills)

        for idx, skill in enumerate(canonical):
            if float(sim[:, idx].max()) >= 0.60:
                enriched.add(skill)

        return list(enriched)
    except:
        return skills


def normalize_skills(skills: List[str]) -> List[str]:
    cleaned = []

    for s in skills:
        s = re.sub(r"[^a-zA-Z0-9 ]", " ", s).strip().lower()
        s = re.sub(r"\s+", " ", s)

        if not s:
            continue

        if s in SKILL_SYNONYMS:
            cleaned.append(SKILL_SYNONYMS[s])
            continue

        cleaned.append(s)

    final = []
    seen = set()
    for s in cleaned:
        if s not in seen:
            final.append(s)
            seen.add(s)
    return final


# ---------------------------------------------------------
# MERGE ALL SKILL SOURCES
# ---------------------------------------------------------
def extract_all_skills(full_text: str, skills_section_text: str) -> List[str]:

    section_tokens = extract_skills_from_section(skills_section_text)

    keyword_based = keyword_skill_extractor(full_text)

    hf_terms = hf_ner.extract_technical_terms(full_text)

    combined = section_tokens + keyword_based + [t.lower() for t in hf_terms]
    combined = list(dict.fromkeys(combined))

    enriched = semantic_skill_enrichment(full_text, combined)

    return normalize_skills(enriched)


# ---------------------------------------------------------
# YEARS + GAP DETECTION
# ---------------------------------------------------------
def extract_years(text: str) -> List[int]:
    years = sorted({int(y) for y in re.findall(r"(19\d{2}|20\d{2})", text)})
    return years

def detect_timeline_gaps(years: List[int]) -> List[str]:
    gaps = []
    for i in range(1, len(years)):
        if years[i] - years[i - 1] > 1:
            gaps.append(f"Gap between {years[i-1]} and {years[i]}")
    return gaps


# ---------------------------------------------------------
# QUALITY SCORE
# ---------------------------------------------------------
def compute_resume_quality(parsed: Dict[str, Any]) -> int:
    score = 50
    score += min(25, len(parsed["skills"]) * 2)
    score += min(20, len(parsed["experience_lines"]) * 2)
    score -= min(10, len(parsed["timeline_gaps"]) * 3)

    wc = len(parsed["raw_text"].split())
    if wc < 120:
        score -= 10
    if wc > 900:
        score += 5

    return max(0, min(100, score))


# ---------------------------------------------------------
# MAIN PARSER
# ---------------------------------------------------------
def parse_resume(file_path: str) -> Dict[str, Any]:
    raw_text = extract_text(file_path)
    sections = detect_sections(raw_text)

    contact = extract_contact(raw_text)

    education = extract_education_entries(sections.get("education", ""))
    experience = extract_experience_entries(sections.get("experience", ""))
    experience_lines = format_experience_lines(experience)

    skills = extract_all_skills(raw_text, sections.get("skills", ""))

    years = extract_years(raw_text)
    gaps = detect_timeline_gaps(years)

    parsed = {
        "file_path": file_path,
        "raw_text": raw_text,
        "contact": contact,
        "education": education,
        "experience": experience,
        "experience_lines": experience_lines,
        "skills": skills,
        "years": years,
        "timeline_gaps": gaps,
    }

    parsed["quality_score"] = compute_resume_quality(parsed)

    return parsed


if __name__ == "__main__":
    import sys
    from pprint import pprint

    if len(sys.argv) < 2:
        print("Usage: python resume_parser.py <resume_path>")
    else:
        pprint(parse_resume(sys.argv[1]))
