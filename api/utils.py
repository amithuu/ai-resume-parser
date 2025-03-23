from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import json


def parse_resume_with_llm(resume_text):
    system_prompt = "You are an expert HR assistant. Extract structured candidate data."
    user_prompt = f"Extract name, skills, experience, education from this resume:\n{resume_text}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        functions=[
            {
                "name": "extract_resume_info",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "skills": {"type": "array", "items": {"type": "string"}},
                        "experience": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "company": {"type": "string"},
                                    "role": {"type": "string"},
                                    "years": {"type": "number"}
                                }
                            }
                        },
                        "education": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["name", "skills"]
                }
            }
        ],
        function_call={"name": "extract_resume_info"}
    )

    arguments = response.choices[0].message.function_call.arguments
    
    return json.loads(arguments)

def parse_job_with_llm(job_description):
    system_prompt = "You are an expert recruiter. Extract required skills from the job description."
    user_prompt = f"Extract job title and required skills from this job description:\n{job_description}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        functions=[{
            "name": "extract_job_info",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "required_skills": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "required_skills"]
            }
        }],
        function_call={"name": "extract_job_info"}
    )
    return eval(response.choices[0].message.function_call.arguments)

def match_candidate_to_job(candidate_data, job_data):
    candidate_skills = set(candidate_data.get('skills', []))
    required_skills = set(job_data.get('required_skills', []))
    match_score = int(len(candidate_skills & required_skills) / len(required_skills) * 100) if required_skills else 0
    missing_skills = list(required_skills - candidate_skills)
    return match_score, missing_skills

def generate_cover_letter(candidate_data, job_data):
    prompt = f"""
    Write a professional cover letter for {candidate_data['name']} applying to {job_data['title']}.
    Candidate skills: {candidate_data['skills']}
    Job requires: {job_data['required_skills']}
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
