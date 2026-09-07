
import textwrap

_SUMMARY_PROMPT = textwrap.dedent("""
You are an expert ATS system and technical recruiter.

Evaluate the candidate's resume against the job description.

Your task is to determine how suitable the candidate is for this position and whether the candidate should be shortlisted.

Evaluate ONLY information explicitly supported by the resume and job description.

Scoring:
- ats_score: 0-100. Measures keyword and ATS alignment with the job description.
- job_match_score: 0-100. Measures the candidate's actual suitability based on skills, experience, education, and responsibilities.

Important rules:
- Do not invent skills, experience, certifications, or qualifications.
- Distinguish between missing skills and missing keywords.
- Missing skills are required abilities not demonstrated by the candidate.
- ATS keyword gaps are relevant terms missing or not explicitly stated in the resume.
- Equivalent technologies or transferable skills should be considered when appropriate.
- Required qualifications should have more weight than preferred qualifications.
- A high ATS score does not automatically mean the candidate is a strong match.

Shortlisting rule:
- If job_match_score >= 80, decision = "SHORTLISTED"
- If job_match_score < 80, decision = "REJECTED"

Return ONLY a valid JSON object.
Do not return markdown.
Do not return code fences.
Do not return explanations outside the JSON.

Return exactly this structure:

{{
  "candidate_summary": "2-3 concise sentences describing the candidate and overall suitability.",
  "ats_score": 0,
  "job_match_score": 0,
  "decision": "SHORTLISTED",
  "top_strengths": [
    "strength 1",
    "strength 2",
    "strength 3"
  ],
  "missing_skills": [
    "skill 1",
    "skill 2",
    "skill 3"
  ],
  "ats_keyword_gaps": [
    "keyword 1",
    "keyword 2",
    "keyword 3"
  ],
  "recommendation": "One concise sentence explaining the recommendation."
}}

Job Description:
{job_description}

Candidate Resume:
{resume}
""")



_SYNTHESIS_PROMPT = """
You are an HR recruiter reviewing multiple candidates for a job position.

You will receive information about {n} candidates.

Candidate information:
{summaries}

Create a final recruitment report.

For each candidate, include:
1. Candidate summary
2. ATS score
3. Job match score
4. Decision (SHORTLISTED or REJECTED)
5. Main strengths
6. Main weaknesses

Then provide:
- A short overall summary
- The best candidates and why they are recommended
- Any candidates that should be rejected and why

Return the result as valid JSON only, using this format:

{{
    "overall_summary": "...",
    "candidates": [
        {{
            "candidate": "...",
            "summary": "...",
            "ats_score": 0,
            "job_match_score": 0,
            "decision": "...",
            "strengths": ["..."],
            "weaknesses": ["..."]
        }}
    ],
    "recommendations": ["..."]
}}
"""


_REVISION_PROMPT = """
You are an HR recruitment reviewer.

You have a current recruitment report and feedback from a human reviewer.

Current Report:
{report}

Human Reviewer Feedback:
{feedback}

Your task is to revise the report based on the human reviewer feedback.

Rules:
1. Keep the information that is still correct.
2. Apply the reviewer's feedback carefully.
3. Do not invent candidate information.
4. Keep the ATS score, job match score, and decision if they are still valid.
5. Change them only if the reviewer feedback requires it.
6. Keep the report clear and professional.
7. Return valid JSON only.
8. Do not add any explanation outside the JSON.

Return the revised report using this structure:

{{
    "overall_summary": "...",
    "candidates": [
        {{
            "candidate": "...",
            "summary": "...",
            "ats_score": 0,
            "job_match_score": 0,
            "decision": "SHORTLISTED or REJECTED",
            "strengths": [],
            "weaknesses": []
        }}
    ],
    "recommendations": []
}}
"""


