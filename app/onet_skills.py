"""
onet_skills.py (UPDATED)
------------------------------------
Lightweight O*NET-style skill extractor.
Now optimized for:
- WordPress ecosystem
- SEO & performance
- Hosting & server skills
- Modern web development stack
"""

import re

class SkillExtractor:
    def __init__(self):

        # Load updated O*NET-style vocabulary
        self.onet_skills = self._load_onet_skill_list()

        # Pre-lowered version for matching
        self.skill_lower = [s.lower() for s in self.onet_skills]

    # ---------------------------------------------------------
    # UPDATED SKILL LIST (WORDPRESS + WEB DEV + HOSTING)
    # ---------------------------------------------------------
    def _load_onet_skill_list(self):
        """
        WordPress / Web Developer enhanced skill vocabulary.
        Lightweight but powerful for ATS extraction.
        """

        return [
            # -------------------------------------
            # WORDPRESS ECOSYSTEM
            # -------------------------------------
            "WordPress", "WooCommerce", "Elementor", "WPBakery",
            "Advanced Custom Fields", "ACF", "Contact Form 7",
            "Theme Development", "Plugin Development",
            "WordPress Core", "Custom Themes", "Custom Plugins",

            # -------------------------------------
            # CORE WEB DEVELOPMENT
            # -------------------------------------
            "HTML", "HTML5", "CSS", "CSS3",
            "JavaScript", "jQuery", "TypeScript",
            "PHP", "MySQL",

            # Bonus frameworks (optional)
            "React", "Vue", "Next.js", "Nuxt.js",

            # -------------------------------------
            # SEO / PERFORMANCE
            # -------------------------------------
            "SEO", "Technical SEO", "On-page SEO",
            "Performance Optimization", "Site Speed Optimization",
            "Caching", "Cache", "Image Optimization",
            "Yoast SEO", "Rank Math",

            # -------------------------------------
            # HOSTING / SERVER / SECURITY
            # -------------------------------------
            "cPanel", "DNS", "FTP", "SSL", "Apache",
            "Nginx", "Cloudflare", "Server Administration",
            "Linux Server", "Hosting Management",

            # -------------------------------------
            # DEVOPS / TOOLS
            # -------------------------------------
            "Git", "GitHub", "GitLab", "Bitbucket",
            "CI/CD", "Docker", "Terminal", "SSH",

            # -------------------------------------
            # SOFT SKILLS (HR Relevant)
            # -------------------------------------
            "Communication", "Teamwork", "Problem Solving",
            "Time Management", "Attention to Detail",
            "Troubleshooting", "Adaptability",

            # -------------------------------------
            # BUSINESS / CLIENT WORK
            # -------------------------------------
            "Client Communication", "Project Management",
            "Requirement Analysis"
        ]

    # ---------------------------------------------------------
    # SKILL EXTRACTION
    # ---------------------------------------------------------
    def extract_skills(self, text: str):
        """
        Extract skills via simple keyword matching.
        Fast + reliable for WordPress/Web Dev resumes.
        """

        t = text.lower()
        found = []

        for skill in self.skill_lower:
            # Exact word boundary match to avoid false hits
            if re.search(rf"\\b{re.escape(skill)}\\b", t):
                found.append(skill)

        return list(sorted(set(found)))

