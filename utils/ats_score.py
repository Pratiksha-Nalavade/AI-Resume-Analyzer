"""
Advanced ATS Compatibility Scoring Engine.
Evaluates resume formatting, section headings, skills, keyword density, action verbs,
quantifiable metrics, and readability to compute an accurate ATS score (0-100).
"""
import re
from utils.skills import extract_skills

# Standard ATS Section Heading synonyms
STANDARD_SECTIONS = {
    "Summary / Profile": [
        r"\b(?:summary|professional summary|executive summary|profile|about me|objective|career objective)\b"
    ],
    "Work Experience": [
        r"\b(?:experience|work experience|professional experience|employment history|work history|career history)\b"
    ],
    "Education": [
        r"\b(?:education|academic background|academics|qualifications|educational qualifications)\b"
    ],
    "Skills": [
        r"\b(?:skills|technical skills|core competencies|technologies|proficiencies|tools & technologies)\b"
    ],
    "Projects": [
        r"\b(?:projects|academic projects|key projects|personal projects|portfolio)\b"
    ],
    "Certifications": [
        r"\b(?:certifications|certificates|licenses|courses|accreditations|training)\b"
    ]
}

# Strong action verbs for resumes
ACTION_VERBS = [
    "led", "engineered", "implemented", "optimized", "developed", "architected",
    "designed", "deployed", "spearheaded", "accelerated", "automated", "created",
    "managed", "collaborated", "built", "enhanced", "resolved", "delivered",
    "integrated", "formulated", "coordinated", "generated", "reduced", "increased"
]


def calculate_ats_score(resume_text, job_description=None):
    """
    Evaluate resume and calculate comprehensive ATS score (0-100) with detailed breakdown.

    Parameters:
        resume_text (str): Extracted resume text.
        job_description (str, optional): Target job description for keyword matching.

    Returns:
        dict: Detailed ATS score breakdown, metrics, and suggestions.
    """
    if not resume_text or not isinstance(resume_text, str) or not resume_text.strip():
        return {
            "total_score": 0,
            "rating": "Needs Improvement",
            "breakdown": {},
            "details": {},
            "suggestions": ["Upload a resume with readable text to calculate ATS score."]
        }

    text = resume_text.strip()
    text_lower = text.lower()
    words = re.findall(r"\b[A-Za-z0-9_+#.-]+\b", text)
    word_count = len(words)

    score_contact = 0
    score_headings = 0
    score_skills = 0
    score_action = 0
    score_formatting = 0
    suggestions = []

    # -------------------------------------------------------------
    # 1. Contact Information & Online Presence (Max 15 pts)
    # -------------------------------------------------------------
    has_email = bool(re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text))
    has_phone = bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text))
    has_link = bool(re.search(r"(linkedin\.com|github\.com|portfolio|http[s]?://)", text_lower))

    if has_email:
        score_contact += 5
    else:
        suggestions.append("Add a professional email address to the resume header.")

    if has_phone:
        score_contact += 5
    else:
        suggestions.append("Include a valid contact phone number with country/area code.")

    if has_link:
        score_contact += 5
    else:
        suggestions.append("Add links to your LinkedIn profile or GitHub/portfolio website.")

    # -------------------------------------------------------------
    # 2. Section Headings (Max 25 pts, 5 pts each for up to 5 sections)
    # -------------------------------------------------------------
    found_sections = []
    missing_sections = []

    for section_name, patterns in STANDARD_SECTIONS.items():
        matched = False
        for p in patterns:
            if re.search(p, text_lower):
                matched = True
                break
        if matched:
            found_sections.append(section_name)
        else:
            missing_sections.append(section_name)

    # Award 5 points per recognized standard section, capped at 25
    sections_count = min(len(found_sections), 5)
    score_headings = sections_count * 5

    if "Work Experience" in missing_sections and "Projects" in missing_sections:
        suggestions.append("Add a distinct 'Work Experience' or 'Projects' section heading.")
    if "Education" in missing_sections:
        suggestions.append("Include an explicitly labeled 'Education' section heading.")
    if "Skills" in missing_sections:
        suggestions.append("Ensure you have a dedicated 'Skills' section heading.")

    # -------------------------------------------------------------
    # 3. Skills & Keywords Density (Max 25 pts)
    # -------------------------------------------------------------
    detected_skills = extract_skills(text)
    skills_count = len(detected_skills)

    if skills_count >= 12:
        skills_points = 25
    elif skills_count >= 8:
        skills_points = 20
    elif skills_count >= 5:
        skills_points = 15
    elif skills_count >= 2:
        skills_points = 10
    else:
        skills_points = 5

    # If job description is provided, adjust with JD overlap
    if job_description and job_description.strip():
        jd_skills = extract_skills(job_description)
        if jd_skills:
            overlap = set(detected_skills).intersection(set(jd_skills))
            overlap_ratio = len(overlap) / len(jd_skills)
            score_skills = int(round(skills_points * 0.5 + (overlap_ratio * 25) * 0.5))
            score_skills = min(25, max(5, score_skills))
            if overlap_ratio < 0.5:
                suggestions.append(f"Incorporate more job-specific keywords. Only {len(overlap)} of {len(jd_skills)} required skills were detected.")
        else:
            score_skills = skills_points
    else:
        score_skills = skills_points

    if skills_count < 8:
        suggestions.append("Enrich the resume with more relevant technical and core industry skills.")

    # -------------------------------------------------------------
    # 4. Action Verbs & Quantifiable Impact (Max 15 pts)
    # -------------------------------------------------------------
    verbs_found = [v for v in ACTION_VERBS if re.search(rf"\b{v}\b", text_lower)]
    metrics_matches = re.findall(r"\b(?:\d+%(?:[\s-]?\w+)?|\$\d+(?:,\d{3})*(?:\.\d+)?|\b\d+\+\s*(?:users|clients|team|projects|requests|stars|downloads|latency)\b)", text_lower)
    metrics_count = len(metrics_matches)

    # Verbs score up to 8 points
    verbs_score = min(8, len(verbs_found) * 2)

    # Metrics score up to 7 points
    metrics_score = min(7, metrics_count * 2) if metrics_count > 0 else (3 if re.search(r"\b\d+\b", text) else 0)

    score_action = min(15, verbs_score + metrics_score)

    if len(verbs_found) < 3:
        suggestions.append("Start bullet points with strong action verbs (e.g. Engineered, Spearheaded, Optimized).")
    if metrics_count == 0:
        suggestions.append("Quantify achievements with measurable numbers, percentages, or metrics (e.g. 'boosted performance by 35%').")

    # -------------------------------------------------------------
    # 5. Formatting & Readability (Max 20 pts)
    # -------------------------------------------------------------
    # Word count: optimal range is 350 - 900 words
    if 350 <= word_count <= 950:
        word_score = 10
    elif 200 <= word_count <= 1300:
        word_score = 7
    else:
        word_score = 4
        if word_count < 200:
            suggestions.append("Resume is too brief. Expand on your project experience and technical responsibilities.")
        elif word_count > 1300:
            suggestions.append("Resume is overly lengthy. Aim for a concise 1-2 page layout (400-800 words).")

    # Bullet points / list format indicator
    has_bullets = bool(re.search(r"[•\-\*]\s+[A-Z]", text)) or (text.count("\n- ") + text.count("\n• ") >= 3)
    bullet_score = 5 if has_bullets else 2
    if not has_bullets:
        suggestions.append("Use standard bullet points for job and project descriptions rather than dense blocks of text.")

    # Sentence length / run-on check
    sentences = re.split(r"[.!?]\s+", text)
    valid_sentences = [s for s in sentences if len(s.split()) > 3]
    long_sentences = [s for s in valid_sentences if len(s.split()) > 35]
    readability_score = 5 if len(long_sentences) <= 2 else 2
    if len(long_sentences) > 2:
        suggestions.append("Break down lengthy, complex sentences into concise, impactful statements.")

    score_formatting = word_score + bullet_score + readability_score

    # -------------------------------------------------------------
    # Total Score Calculation
    # -------------------------------------------------------------
    total_score = score_contact + score_headings + score_skills + score_action + score_formatting
    total_score = max(5, min(100, total_score))

    if total_score >= 80:
        rating = "Excellent"
    elif total_score >= 65:
        rating = "Good"
    else:
        rating = "Needs Improvement"

    return {
        "total_score": total_score,
        "rating": rating,
        "breakdown": {
            "contact_info": {
                "score": score_contact,
                "max": 15,
                "label": "Contact & Links",
                "status": "Pass" if score_contact >= 10 else "Needs Work"
            },
            "headings": {
                "score": score_headings,
                "max": 25,
                "label": "Section Headings",
                "status": "Pass" if score_headings >= 20 else "Needs Work"
            },
            "skills_keywords": {
                "score": score_skills,
                "max": 25,
                "label": "Skills & Keywords",
                "status": "Pass" if score_skills >= 18 else "Needs Work"
            },
            "action_impact": {
                "score": score_action,
                "max": 15,
                "label": "Action Verbs & Impact",
                "status": "Pass" if score_action >= 10 else "Needs Work"
            },
            "readability_format": {
                "score": score_formatting,
                "max": 20,
                "label": "Formatting & Readability",
                "status": "Pass" if score_formatting >= 15 else "Needs Work"
            }
        },
        "details": {
            "word_count": word_count,
            "skills_detected": detected_skills,
            "action_verbs_found": verbs_found,
            "sections_found": found_sections,
            "missing_sections": missing_sections,
            "metrics_count": metrics_count
        },
        "suggestions": suggestions
    }
