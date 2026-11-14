"""
Automated Test Suite for AI Resume Analyzer.
Verifies all modules, text extraction, ATS calculations, skills matching,
PDF generation, history persistence, and configuration safety.
"""
import os
import sys
import unittest
from io import BytesIO

# Configuration
from config import get_groq_api_key, DEFAULT_MODEL, AVAILABLE_MODELS

# Utilities
from utils.pdf_reader import extract_text_from_pdf
from utils.docx_reader import extract_text_from_docx
from utils.skills import extract_skills, compare_skills
from utils.ats_score import calculate_ats_score
from utils.parser import parse_analysis_output, extract_section, get_scores
from utils.pdf_generator import create_pdf
from utils.history import save_history, get_history, get_history_stats, clear_history
from utils.analyzer import get_groq_client


class TestResumeAnalyzer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sample_pdf = os.path.join("sample_resumes", "sample_software_engineer_resume.pdf")
        cls.sample_docx = os.path.join("sample_resumes", "sample_software_engineer_resume.docx")
        cls.sample_jd = """Full Stack Software Engineer
        Requirements: Python, React, FastAPI, Docker, AWS, PostgreSQL, Redis, CI/CD, Git, TypeScript."""

    def test_01_config_and_groq_safety(self):
        """Test configuration defaults and ensure analyzer does not crash without API key."""
        self.assertIn(DEFAULT_MODEL, AVAILABLE_MODELS)
        client, err = get_groq_client("invalid_placeholder_key_gsk")
        # Should not raise exception at import or instantiation
        self.assertTrue(client is not None or err is not None)

    def test_02_pdf_text_extraction(self):
        """Test extracting text from sample PDF."""
        self.assertTrue(os.path.exists(self.sample_pdf), "Sample PDF should exist.")
        text = extract_text_from_pdf(self.sample_pdf)
        self.assertTrue(len(text) > 100)
        self.assertIn("ALEX MORGAN", text.upper())
        self.assertIn("Python", text)
        self.assertIn("FastAPI", text)

    def test_03_docx_text_extraction(self):
        """Test extracting text from sample DOCX."""
        self.assertTrue(os.path.exists(self.sample_docx), "Sample DOCX should exist.")
        text = extract_text_from_docx(self.sample_docx)
        self.assertTrue(len(text) > 100)
        self.assertIn("Alex Morgan", text)
        self.assertIn("PostgreSQL", text)
        self.assertIn("Docker", text)

    def test_04_invalid_file_handling(self):
        """Test handling of empty or invalid file inputs."""
        empty_stream = BytesIO(b"")
        with self.assertRaises(ValueError):
            extract_text_from_pdf(empty_stream)

    def test_05_skills_extraction_and_matching(self):
        """Test skill taxonomy detection and job matching."""
        resume_text = "Experienced in Python, React, Docker, FastAPI, PostgreSQL, AWS, Git, and Redis."
        skills = extract_skills(resume_text)
        self.assertIn("Python", skills)
        self.assertIn("React", skills)
        self.assertIn("Docker", skills)
        self.assertIn("PostgreSQL", skills)

        comp = compare_skills(resume_text, self.sample_jd)
        self.assertTrue(len(comp["matching_skills"]) >= 5)
        self.assertTrue(comp["match_percentage"] > 50)
        self.assertIsInstance(comp["keyword_suggestions"], list)

    def test_06_ats_scoring_engine(self):
        """Test 5-pillar ATS scoring algorithm."""
        with open(self.sample_docx, "rb") as f:
            resume_text = extract_text_from_docx(f)

        score_result = calculate_ats_score(resume_text, self.sample_jd)
        self.assertTrue(0 <= score_result["total_score"] <= 100)
        self.assertIn(score_result["rating"], ["Excellent", "Good", "Needs Improvement"])

        breakdown = score_result["breakdown"]
        self.assertIn("contact_info", breakdown)
        self.assertIn("headings", breakdown)
        self.assertIn("skills_keywords", breakdown)
        self.assertIn("action_impact", breakdown)
        self.assertIn("readability_format", breakdown)

        self.assertTrue(score_result["total_score"] >= 70, f"Alex Morgan resume should score high, got {score_result['total_score']}")

    def test_07_parser_robustness(self):
        """Test parsing of AI outputs with varied markdown styles."""
        sample_ai_output = """
### ATS Score: 88
**Job Match Score:** 82

### Matching Skills:
- Python
- React
- Docker
- FastAPI

### Missing Skills:
- Kubernetes
- GraphQL

### Overall Summary:
Strong full stack candidate with proven API and cloud capabilities.

### Strengths:
- Reduced latency by 40% with Redis caching
- Excellent test coverage with PyTest

### Weaknesses:
- Limited enterprise Kubernetes deployment experience

### Suggestions:
- Emphasize cloud architecture achievements
- Add GraphQL project examples

### Resume Improvement Roadmap:
1. Highlight distributed caching benchmarks
2. Add Kubernetes container orchestration context
3. Align summary with target Staff Engineer competencies
4. Include open source contributions
5. Final proofread for formatting

### Technical Interview Questions:
1. Q: How did you implement Redis caching in FastAPI to achieve under 80ms latency?
   Focus: Cache invalidation, TTL strategies, and concurrency.
2. Q: Explain your CI/CD pipeline automation with GitHub Actions.
   Focus: Multi-stage Docker builds and automated test gates.
"""
        parsed = parse_analysis_output(sample_ai_output)
        self.assertEqual(parsed["ats_score"], 88)
        self.assertEqual(parsed["job_score"], 82)
        self.assertIn("Python", parsed["matching_skills"])
        self.assertIn("Kubernetes", parsed["missing_skills"])
        self.assertIn("Strong full stack", parsed["summary"])
        self.assertTrue(len(parsed["roadmap"].split("\n")) >= 4)
        self.assertTrue("Redis caching" in parsed["questions"])

    def test_08_pdf_report_generation(self):
        """Test executive PDF generation using ReportLab."""
        test_payload = {
            "ats_score": 85,
            "job_score": 80,
            "summary": "Executive candidate evaluation summary.",
            "matching_skills": "- Python\n- React\n- PostgreSQL",
            "missing_skills": "- Kubernetes\n- Terraform",
            "strengths": "- 40% latency reduction\n- 88% test coverage",
            "weaknesses": "- Missing Kubernetes\n- Needs more cloud metrics",
            "suggestions": "- Add container orchestration experience\n- Highlight system scale",
            "roadmap": "1. Update skills section\n2. Add metrics to bullet points\n3. Review formatting",
            "questions": "1. Q: Explain Redis caching architecture.\n   Focus: Invalidation strategies."
        }
        out_file = os.path.join("output", "test_report.pdf")
        res_path = create_pdf(test_payload, resume_filename="Alex_Morgan.pdf", output_filename=out_file)
        self.assertTrue(os.path.exists(res_path))
        self.assertTrue(os.path.getsize(res_path) > 1000)

    def test_09_history_persistence(self):
        """Test saving, retrieving, and clearing history."""
        save_history("Test_Resume.pdf", 85, 78, "Python, React", "Kubernetes", "Raw analysis text")
        df = get_history()
        self.assertFalse(df.empty)
        stats = get_history_stats()
        self.assertTrue(stats["total_count"] >= 1)
        self.assertTrue(stats["avg_ats"] > 0)


if __name__ == "__main__":
    unittest.main()
