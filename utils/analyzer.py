"""
Groq AI Resume Analyzer module.
Handles AI-powered resume evaluation, job matching, recommendations, and interview prep.
"""
from groq import Groq
from config import get_groq_api_key, get_selected_model, DEFAULT_MODEL


def get_groq_client(api_key=None):
    """
    Initialize Groq client safely with the provided or discovered API key.

    Returns:
        tuple[Groq | None, str | None]: (client_instance, error_message)
    """
    key = (api_key or get_groq_api_key() or "").strip()
    if not key or key == "gsk_your_groq_api_key_here":
        return None, "Groq API Key not found. Please provide a valid key in .env or Settings."

    try:
        client = Groq(api_key=key)
        return client, None
    except Exception as e:
        return None, f"Failed to initialize Groq client: {e}"


def test_groq_connection(api_key=None, model=None):
    """
    Test connectivity to Groq API.

    Returns:
        tuple[bool, str]: (is_successful, message)
    """
    client, error = get_groq_client(api_key)
    if client is None:
        return False, error

    target_model = model or get_selected_model() or DEFAULT_MODEL

    try:
        try:
            response = client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "user", "content": "Ping test. Reply with 'OK'."}
                ],
                max_tokens=10,
                temperature=0.1,
            )
        except Exception as model_err:
            err_lower = str(model_err).lower()
            if "model_not_found" in err_lower or "does not exist" in err_lower or "access" in err_lower:
                account_models = [m.id for m in client.models.list().data]
                candidates = ["qwen/qwen3.8-27b", "llama-3.1-8b-instant", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]
                fallback = next((c for c in candidates if c in account_models and c != target_model), None)
                if fallback:
                    target_model = fallback
                    response = client.chat.completions.create(
                        model=target_model,
                        messages=[
                            {"role": "user", "content": "Ping test. Reply with 'OK'."}
                        ],
                        max_tokens=10,
                        temperature=0.1,
                    )
                else:
                    raise model_err
            else:
                raise model_err

        reply = response.choices[0].message.content.strip()
        return True, f"Connection successful! Model '{target_model}' responded: {reply}"
    except Exception as e:
        return False, f"Groq API Error: {str(e)}"


def analyze_resume(resume_text, job_description, api_key=None, model=None):
    """
    Analyze resume against job description using Groq LLM.

    Parameters:
        resume_text (str): Extracted resume text.
        job_description (str): Target job description text.
        api_key (str, optional): Groq API key override.
        model (str, optional): Groq model override.

    Returns:
        str: AI analysis output.

    Raises:
        ValueError: If inputs or API key are invalid.
        RuntimeError: If Groq API request fails.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty or could not be read.")

    if not job_description or not job_description.strip():
        raise ValueError("Job description is empty. Please provide target job details.")

    client, error = get_groq_client(api_key)
    if client is None:
        raise ValueError(error)

    selected_model = model or get_selected_model() or DEFAULT_MODEL

    prompt = f"""
You are an executive ATS Resume Evaluation Specialist, Senior Technical Recruiter, and Career Coach.

Your task is to conduct an in-depth, rigorous evaluation of the candidate's resume against the target job description.

EVALUATION CRITERIA:
1. ATS Score (0-100): Evaluate resume structure, standard headings, technical/soft skills density, readability, bullet points, and contact info completeness.
2. Job Match Score (0-100): Directly measure the percentage alignment between candidate's qualifications/experience and the target job description's required skills and responsibilities.
3. Matching Skills: Specific technical, tools, domain, and soft skills present in BOTH the resume and job description.
4. Missing Skills: Essential qualifications, skills, frameworks, or tools required by the job that are missing or underrepresented in the resume.
5. Overall Summary: A concise 2-3 sentence executive appraisal of the candidate's fit for this role.
6. Strengths: 3 to 5 notable strengths evident in the candidate's background, projects, or metrics.
7. Weaknesses: 2 to 4 key gaps, missing qualifications, or resume presentation shortcomings.
8. Suggestions: 3 to 5 clear, high-impact, actionable recommendations to improve the resume for this position.
9. Resume Improvement Roadmap: Exactly 5 progressive, prioritized action items to optimize the resume before applying.
10. Technical Interview Questions: Exactly 5 targeted technical or architectural interview questions directly based on the candidate's stated projects and the job requirements, each with a brief note on what the interviewer looks for.

CRITICAL FORMAT REQUIREMENT:
You must strictly follow this format with exact section headings:

ATS Score: [number between 0 and 100]
Job Match Score: [number between 0 and 100]

Matching Skills:
- [Skill 1]
- [Skill 2]
- [Skill 3]
...

Missing Skills:
- [Skill 1]
- [Skill 2]
- [Skill 3]
...

Overall Summary:
[Concise executive evaluation summary paragraph]

Strengths:
- [Strength 1 with context]
- [Strength 2 with context]
- [Strength 3 with context]

Weaknesses:
- [Weakness 1 with context]
- [Weakness 2 with context]

Suggestions:
- [Actionable suggestion 1]
- [Actionable suggestion 2]
- [Actionable suggestion 3]

Resume Improvement Roadmap:
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]
4. [Action item 4]
5. [Action item 5]

Technical Interview Questions:
1. Q: [Question based on candidate's project/skill]
   Focus: [What a strong answer should demonstrate]
2. Q: [Question based on candidate's project/skill]
   Focus: [What a strong answer should demonstrate]
3. Q: [Question based on candidate's project/skill]
   Focus: [What a strong answer should demonstrate]
4. Q: [Question based on candidate's project/skill]
   Focus: [What a strong answer should demonstrate]
5. Q: [Question based on candidate's project/skill]
   Focus: [What a strong answer should demonstrate]

---
CANDIDATE RESUME:
{resume_text}

---
TARGET JOB DESCRIPTION:
{job_description}
"""

    try:
        try:
            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional ATS resume analyzer and career coach. "
                            "Provide objective, realistic, and highly actionable analysis without generic boilerplate."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500,
            )
        except Exception as model_err:
            err_lower = str(model_err).lower()
            if "model_not_found" in err_lower or "does not exist" in err_lower or "access" in err_lower:
                account_models = [m.id for m in client.models.list().data]
                candidates = ["qwen/qwen3.8-27b", "llama-3.1-8b-instant", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]
                fallback = next((c for c in candidates if c in account_models and c != selected_model), None)
                if fallback:
                    response = client.chat.completions.create(
                        model=fallback,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a professional ATS resume analyzer and career coach. "
                                    "Provide objective, realistic, and highly actionable analysis without generic boilerplate."
                                )
                            },
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=2500,
                    )
                else:
                    raise model_err
            else:
                raise model_err

        content = response.choices[0].message.content
        if not content or not content.strip():
            raise RuntimeError("Received an empty response from Groq API.")

        return content.strip()

    except Exception as e:
        error_msg = str(e)
        if "invalid_api_key" in error_msg.lower() or "401" in error_msg:
            raise RuntimeError("Invalid Groq API key. Please verify your API key in Settings or .env.")
        elif "rate_limit" in error_msg.lower() or "429" in error_msg:
            raise RuntimeError("Groq API rate limit reached. Please wait a moment before trying again.")
        else:
            raise RuntimeError(f"Groq API Error: {error_msg}")
