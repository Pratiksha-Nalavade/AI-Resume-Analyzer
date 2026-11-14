"""
Comprehensive Skills Taxonomy and Matching Engine.
Provides skill extraction, normalization, and job-resume matching.
"""
import re

# Comprehensive skill catalog organized by domain
SKILLS_CATALOG = {
    "Programming Languages": [
        "Python", "Java", "C++", "C#", "C", "JavaScript", "TypeScript", "Go", "Golang",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "SQL", "HTML", "HTML5", "CSS", "CSS3",
        "R", "MATLAB", "Scala", "Dart", "Shell", "Bash", "Perl", "PowerShell"
    ],
    "Frontend Development": [
        "React", "React.js", "Next.js", "Angular", "Vue", "Vue.js", "Nuxt.js", "Svelte",
        "Redux", "Tailwind CSS", "Bootstrap", "Material-UI", "Sass", "LESS", "Webpack",
        "Vite", "jQuery", "Responsive Design", "DOM Manipulation"
    ],
    "Backend & APIs": [
        "Node.js", "Express", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot",
        "ASP.NET", "Ruby on Rails", "NestJS", "GraphQL", "REST", "RESTful APIs", "Microservices",
        "gRPC", "WebSockets", "Celery", "Kafka", "RabbitMQ"
    ],
    "Databases & Storage": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle", "Microsoft SQL Server",
        "DynamoDB", "Cassandra", "Elasticsearch", "Firebase", "Supabase", "Snowflake",
        "BigQuery", "Neo4j"
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes",
        "Terraform", "CI/CD", "GitHub Actions", "Jenkins", "GitLab CI", "Ansible", "Linux",
        "Nginx", "Apache", "Prometheus", "Grafana", "CloudFormation", "Serverless"
    ],
    "Data Science & AI / ML": [
        "Machine Learning", "Deep Learning", "Natural Language Processing", "NLP",
        "Computer Vision", "PyTorch", "TensorFlow", "Scikit-Learn", "Pandas", "NumPy",
        "Keras", "Hugging Face", "LLMs", "Large Language Models", "Generative AI", "GenAI",
        "LangChain", "RAG", "Data Analysis", "Data Visualization", "Matplotlib", "Seaborn",
        "Groq", "OpenAI", "Prompt Engineering"
    ],
    "Tools & Methodologies": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Agile", "Scrum",
        "Kanban", "TDD", "Test-Driven Development", "Postman", "Swagger", "Docker Compose",
        "Unit Testing", "PyTest", "Jest", "CI/CD Pipelines", "Figma"
    ],
    "Soft Skills": [
        "Communication", "Leadership", "Problem Solving", "Team Collaboration", "Teamwork",
        "Time Management", "Critical Thinking", "Adaptability", "Mentorship", "Project Management",
        "Analytical Skills", "Attention to Detail", "Decision Making"
    ]
}

# Flatten catalog and prepare regex patterns
CANONICAL_SKILLS = {}
for category, skills in SKILLS_CATALOG.items():
    for skill in skills:
        CANONICAL_SKILLS[skill.lower()] = skill


def extract_skills(text):
    """
    Extract recognized skills from text using boundary-safe matching.

    Parameters:
        text (str): Resume or job description text.

    Returns:
        list[str]: Sorted list of unique canonical skills found.
    """
    if not text or not isinstance(text, str):
        return []

    found_skills = set()
    text_lower = " " + text.lower() + " "

    # Check each skill in canonical dictionary
    for skill_lower, skill_canonical in CANONICAL_SKILLS.items():
        # Escape special chars like ++, #, .
        escaped = re.escape(skill_lower)
        pattern = rf"(?<![a-zA-Z0-9_#+.-]){escaped}(?![a-zA-Z0-9_#+.-])"
        if re.search(pattern, text_lower):
            found_skills.add(skill_canonical)

    return sorted(list(found_skills))


def compare_skills(resume_text, job_description_text):
    """
    Compare skills found in resume against skills required in job description.

    Returns:
        dict:
            - matching_skills (list[str])
            - missing_skills (list[str])
            - additional_skills (list[str])
            - match_percentage (int 0-100)
            - keyword_suggestions (list[str])
    """
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description_text))

    matching = sorted(list(resume_skills.intersection(job_skills)))
    missing = sorted(list(job_skills.difference(resume_skills)))
    additional = sorted(list(resume_skills.difference(job_skills)))

    if len(job_skills) > 0:
        match_score = int(round((len(matching) / len(job_skills)) * 100))
    else:
        # If JD has no recognized skills or is short, calculate based on general keyword overlap
        words_job = set(re.findall(r"\b[A-Za-z]{3,}\b", job_description_text.lower()))
        words_resume = set(re.findall(r"\b[A-Za-z]{3,}\b", resume_text.lower()))
        common = words_job.intersection(words_resume)
        match_score = int(round((len(common) / max(len(words_job), 1)) * 100)) if words_job else 50
        match_score = max(10, min(95, match_score))

    match_score = max(0, min(100, match_score))

    # Suggested keywords are the top missing skills
    keyword_suggestions = missing[:10]

    return {
        "matching_skills": matching,
        "missing_skills": missing,
        "additional_skills": additional,
        "match_percentage": match_score,
        "keyword_suggestions": keyword_suggestions
    }
