# AI Recruiter & Talent Assessment Platform

An AI-driven B2B SaaS platform designed to automate and streamline the modern hiring workflow. Built with **Streamlit**, **OpenAI**, **DeepSeek**, and **Hugging Face**, the platform delivers end-to-end recruitment automation—from intelligent resume parsing and standardized skill matching using the O*NET database to machine-learning-based candidate ranking and interactive AI mock interviews.

---

## 🌟 Key Features

* **📄 Automated Resume Parsing:** Extracts key candidate data, work experience, education, and technical skills directly from uploaded resumes (PDF/Word).
* **🎯 O*NET Taxonomy Skill Mapping:** Standardizes extracted candidate skills against the official O*NET occupational database to eliminate terminology mismatches.
* **📊 ML Candidate Ranking Engine:** Leverages a custom predictive machine learning model (`ranking_model.pkl`) to score and rank candidates against specific job descriptions.
* **🤖 Interactive AI Interviewer:** Generates dynamic, context-aware technical and behavioral interview questions based on candidate profiles and role requirements.
* **🎥 Video & Interactive Evaluation Modules:** Dedicated UI components for conducting structured online assessments and video interviews.
* **⚡ Multi-Model LLM Integration:** Combines OpenAI and DeepSeek models for deep natural language understanding, skill extraction, and conversational interviewing.

---

## 🏗️ Architecture & Tech Stack

* **Frontend UI & Dashboard:** [Streamlit](https://streamlit.io/)
* **AI & Natural Language Processing:** OpenAI API, DeepSeek API, Hugging Face Transformers
* **Machine Learning & Scoring:** Python, Scikit-Learn (`ranking_engine.py`, `ranking_model.pkl`)
* **Data Standards:** O*NET OnLine Competency Framework (`onet_skills.py`)

---

## 📁 Repository Structure

```text
FinalYearProject/
│
├── app/
│   ├── .streamlit/             # App configuration & local secrets
│   ├── huggingface_extractor.py# Hugging Face model integration
│   ├── interview_engine.py     # Core interview logic & prompt orchestration
│   ├── interview_tab.py        # Streamlit tab UI for live interviews
│   ├── job_matcher.py          # Job description matching algorithms
│   ├── onet_skills.py          # O*NET skill taxonomy integration
│   ├── openai_config.py        # API client configuration
│   ├── ranking_engine.py       # Candidate scoring engine
│   ├── ranking_model.pkl       # Trained ML ranking model
│   ├── resume_parser.py        # PDF & document extraction tools
│   ├── streamlit_app.py        # Main entry point for the Streamlit dashboard
│   └── video_interview.py      # Video assessment module
│
├── .gitignore                  # Git tracking rules
└── README.md                   # Project documentation
