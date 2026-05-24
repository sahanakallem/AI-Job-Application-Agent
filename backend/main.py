from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import Counter
from typing import List
import re


app = FastAPI(title="AI Job Application Agent")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobAnalysisRequest(BaseModel):
    job_title: str
    company_name: str
    job_description: str
    resume_text: str


class Requirement(BaseModel):
    keyword: str
    category: str


class JobAnalysisResponse(BaseModel):
    match_score: int
    job_requirements: List[Requirement]
    matched_keywords: List[str]
    missing_keywords: List[str]
    resume_keywords: List[str]
    suggested_resume_bullets: List[str]
    application_answer: str
    agent_steps: List[str]


STOP_WORDS = {
    "the", "and", "for", "with", "you", "your", "our", "are", "will", "this",
    "that", "have", "has", "from", "not", "but", "all", "can", "who", "they",
    "their", "about", "into", "more", "such", "using", "use", "used", "work",
    "working", "team", "teams", "role", "job", "experience", "years", "year",
    "skills", "ability", "strong", "good", "excellent", "responsibilities",
    "requirements", "preferred", "required", "including", "across", "within",
    "build", "building", "develop", "development", "solutions", "systems",
    "business", "product", "products", "services", "support", "help", "new",
    "design", "designing", "based", "related", "knowledge", "understanding",
}


TECH_KEYWORDS = {
    "python", "java", "javascript", "typescript", "react", "angular", "node",
    "node.js", "express", "spring", "spring boot", "fastapi", "django", "flask",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
    "github actions", "ci/cd", "postgresql", "mysql", "mongodb", "dynamodb",
    "redis", "kafka", "graphql", "rest", "rest api", "microservices",
    "lambda", "api gateway", "s3", "cloudwatch", "cognito", "sql", "nosql",
    "machine learning", "deep learning", "llm", "rag", "langchain",
    "openai", "pandas", "numpy", "pytorch", "tensorflow",
}


SOFT_SKILLS = {
    "communication", "collaboration", "leadership", "ownership",
    "problem solving", "analytical", "stakeholder", "cross-functional",
    "agile", "scrum", "mentoring", "debugging", "troubleshooting",
}


ACTION_VERBS = [
    "built", "developed", "implemented", "designed", "optimized",
    "improved", "automated", "integrated", "delivered", "maintained",
]


def normalize_text(text: str) -> str:
    return text.lower().replace("–", "-").replace("—", "-")


def extract_phrases(text: str) -> List[str]:
    text = normalize_text(text)

    phrases = set()

    known_phrases = TECH_KEYWORDS.union(SOFT_SKILLS)
    for phrase in known_phrases:
        if phrase in text:
            phrases.add(phrase)

    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.\-]{1,}\b", text)
    filtered_words = [
        word.lower()
        for word in words
        if word.lower() not in STOP_WORDS and len(word) > 2
    ]

    word_counts = Counter(filtered_words)

    for word, count in word_counts.most_common(40):
        if count >= 2:
            phrases.add(word)

    return sorted(phrases)


def categorize_requirement(keyword: str) -> str:
    if keyword in TECH_KEYWORDS:
        return "technical"
    if keyword in SOFT_SKILLS:
        return "soft skill"
    if keyword in {"agile", "scrum", "ci/cd", "debugging", "troubleshooting"}:
        return "workflow"
    return "domain/general"


def extract_job_requirements(job_description: str) -> List[Requirement]:
    keywords = extract_phrases(job_description)

    requirements = [
        Requirement(keyword=keyword, category=categorize_requirement(keyword))
        for keyword in keywords
    ]

    priority_order = {
        "technical": 1,
        "workflow": 2,
        "soft skill": 3,
        "domain/general": 4,
    }

    requirements.sort(key=lambda item: (priority_order.get(item.category, 5), item.keyword))

    return requirements[:30]


def extract_resume_keywords(resume_text: str) -> List[str]:
    return extract_phrases(resume_text)


def compare_resume_to_job(job_requirements: List[Requirement], resume_keywords: List[str]):
    resume_keyword_set = set(resume_keywords)

    matched = []
    missing = []

    for requirement in job_requirements:
        if requirement.keyword in resume_keyword_set:
            matched.append(requirement.keyword)
        else:
            missing.append(requirement.keyword)

    total = len(matched) + len(missing)

    if total == 0:
        score = 0
    else:
        score = round((len(matched) / total) * 100)

    return score, matched, missing


def generate_resume_bullets(
    job_title: str,
    matched_keywords: List[str],
    missing_keywords: List[str],
) -> List[str]:
    strongest_keywords = matched_keywords[:5]
    missing_focus = missing_keywords[:4]

    if strongest_keywords:
        skills_text = ", ".join(strongest_keywords)
    else:
        skills_text = "backend systems, APIs, debugging, and application development"

    bullets = [
        f"Developed and maintained application features aligned with {job_title} responsibilities, using {skills_text} to improve reliability and delivery speed.",
        "Collaborated with cross-functional teams in Agile sprints to analyze requirements, implement features, review code, and support production-ready releases.",
        "Improved backend and application workflows by debugging issues, validating API behavior, and strengthening maintainability across the software delivery lifecycle.",
    ]

    if missing_focus:
        bullets.append(
            f"Recommended resume improvement: add evidence for {', '.join(missing_focus)} if you have real experience with these areas."
        )

    return bullets


def generate_application_answer(
    job_title: str,
    company_name: str,
    matched_keywords: List[str],
) -> str:
    if matched_keywords:
        skill_summary = ", ".join(matched_keywords[:4])
    else:
        skill_summary = "software development, problem solving, and application delivery"

    return (
        f"I am interested in the {job_title} role at {company_name} because it aligns with my background in "
        f"{skill_summary}. I enjoy building reliable applications, collaborating with teams, and turning business "
        f"requirements into practical technical solutions. This role feels like a strong opportunity to contribute "
        f"while continuing to grow as an engineer."
    )


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "AI Job Application Agent backend is running",
    }


@app.post("/analyze-job", response_model=JobAnalysisResponse)
def analyze_job(request: JobAnalysisRequest):
    agent_steps = []

    agent_steps.append("Step 1: Received resume and job description.")
    job_requirements = extract_job_requirements(request.job_description)

    agent_steps.append("Step 2: Extracted dynamic job requirements from the job description.")
    resume_keywords = extract_resume_keywords(request.resume_text)

    agent_steps.append("Step 3: Extracted candidate keywords from the resume.")
    match_score, matched_keywords, missing_keywords = compare_resume_to_job(
        job_requirements,
        resume_keywords,
    )

    agent_steps.append("Step 4: Compared resume keywords against job requirements.")
    suggested_resume_bullets = generate_resume_bullets(
        request.job_title,
        matched_keywords,
        missing_keywords,
    )

    agent_steps.append("Step 5: Generated resume tailoring suggestions.")
    application_answer = generate_application_answer(
        request.job_title,
        request.company_name,
        matched_keywords,
    )

    agent_steps.append("Step 6: Generated a short application response.")

    return JobAnalysisResponse(
        match_score=match_score,
        job_requirements=job_requirements,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        resume_keywords=resume_keywords[:30],
        suggested_resume_bullets=suggested_resume_bullets,
        application_answer=application_answer,
        agent_steps=agent_steps,
    )