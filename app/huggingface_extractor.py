# huggingface_extractor.py
"""

"""

from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TokenClassificationPipeline,
)

NER_MODEL = "dslim/bert-base-NER"


class HF_NER_SkillExtractor:
    def __init__(self):
        print("Loading HuggingFace NER model (dslim/bert-base-NER)...")
        self.tokenizer = AutoTokenizer.from_pretrained(NER_MODEL)
        self.model = AutoModelForTokenClassification.from_pretrained(NER_MODEL)
        self.pipeline = TokenClassificationPipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",
        )

    def extract_entities(self, text: str):
        """Return all labeled entities from the text."""
        if not text.strip():
            return []
        return self.pipeline(text)

    def extract_names(self, text: str):
        """Return PERSON entities detected in the text."""
        ents = self.extract_entities(text)
        names = [e["word"] for e in ents if e.get("entity_group") == "PER"]
        # small clean-up
        cleaned = []
        for n in names:
            n = n.replace("#", "").strip()
            if n and n not in cleaned:
                cleaned.append(n)
        return cleaned

    def extract_technical_terms(self, text: str):
        """
        Use NER entities as candidate spans, then filter by
        tech-related patterns. This is a helper, not the only
        skill extraction method (we still also use keyword DB).
        """
        ents = self.extract_entities(text)
        candidates = [e["word"].lower().replace("#", "").strip() for e in ents]

        TECH_HINTS = [
            "python", "java", "c#", "c++", ".net", "asp.net", "sql", "javascript",
            "typescript", "react", "angular", "node", "django", "flask",
            "aws", "azure", "docker", "kubernetes", "git", "linux",
            "raven", "salesforce", "jira"
        ]

        found = []
        for c in candidates:
            for h in TECH_HINTS:
                if h in c:
                    found.append(h)
        # dedupe
        found = list(dict.fromkeys(found))
        return found


if __name__ == "__main__":
    extractor = HF_NER_SkillExtractor()
    sample = "Senior .NET Developer with C#, ASP.NET Core, SQL Server, Angular, and Azure."
    print("Names:", extractor.extract_names(sample))
    print("Tech terms:", extractor.extract_technical_terms(sample))
