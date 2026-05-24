from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="AI Job Application Agent")


class JobAnalysisRequest(BaseModel):
    job_title: str
    company_name: str
    job_description: str
    resume_text: str


class JobAnalysisResponse(BaseModel):
    match_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    suggested_bullets: List[str]
    application_answer: str


@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Job Application Agent backend is running"}


@app.post("/analyze-job", response_model=JobAnalysisResponse)
def analyze_job(request: JobAnalysisRequest):
    job_text = request.job_description.lower()
    resume_text = request.resume_text.lower()

    target_skills = [
        "java",
        "python",
        "react",
        "typescript",
        "javascript",
        "spring boot",
        "fastapi",
        "aws",
        "docker",
        "kubernetes",
        "postgresql",
        "dynamodb",
        "rest api",
        "graphql",
        "ci/cd",
        "microservices",
    ]

    matched_skills = [
        skill for skill in target_skills
        if skill in job_text and skill in resume_text
    ]

    missing_skills = [
        skill for skill in target_skills
        if skill in job_text and skill not in resume_text
    ]

    match_score = int((len(matched_skills) / max(len(matched_skills) + len(missing_skills), 1)) * 100)

    suggested_bullets = [
        f"Built and maintained backend services for {request.job_title} workflows using scalable APIs and cloud-based architecture.",
        "Improved application reliability by debugging API failures, monitoring logs, and supporting CI/CD deployment workflows.",
        "Collaborated in Agile sprints to deliver full-stack features across frontend, backend, and database layers.",
    ]

    application_answer = (
        f"I am interested in the {request.job_title} role at {request.company_name} "
        f"because it aligns with my experience in backend development, cloud-based systems, "
        f"API design, and full-stack application delivery."
    )

    return JobAnalysisResponse(
        match_score=match_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        suggested_bullets=suggested_bullets,
        application_answer=application_answer,
    )