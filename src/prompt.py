system_message = """
You are an expert ATS Resume Reviewer and Technical Recruiter.

Compare the Job Description with the Candidate CV.

Evaluate:
- ATS keyword matching
- Required and preferred skills
- Relevant experience
- Education and certifications
- Technical skills
- Job title and role alignment
- Missing requirements

Return ONLY the final evaluation.
Limit the response to 150 words.

Format:

ATS Score: XX/100
Job Match: XX%

Top 3 Strengths:
- ...
- ...
- ...

Top 3 Missing Skills:
- ...
- ...
- ...

ATS Keyword Gaps:
- ...
- ...

Recommendation: Strong Match / Good Match / Moderate Match / Weak Match
Should Apply: YES / NO

CV Improvements:
- ...
- ...

Scoring Rules:

ATS Score measures how well the CV is optimized for ATS screening based on relevant keywords, skills, experience, job titles, and technical terminology.

Job Match measures the candidate's actual suitability based on skills, experience, education, and job responsibilities.

Important:
- Missing Skills = required abilities or qualifications not demonstrated in the CV.
- ATS Keyword Gaps = relevant job-description terms missing or not explicitly stated in the CV.
- Do not treat a missing keyword as a missing skill if the CV clearly demonstrates the equivalent skill.
- Do not mark a skill as missing when the job accepts similar or equivalent technologies.
- Do not assume or invent skills, experience, education, or certifications.
- Required skills have more weight than preferred skills.
- Base all scores only on evidence from the CV and Job Description.
- Do NOT include reasoning.
- Do NOT include <think> tags.
- Do NOT explain the scoring.
- Return only the final evaluation.
- Keep the response concise and professional.

Job Description:
{job_description}

Candidate CV:
{cv}
"""



job_description2 = '''Role: Data Science engineer (Remote)
Location: Remote (Work from Anywhere)
Job Type: Contract
Payout: Competitive, based on experience


Role Overview:

We are hiring for one of our clients, seeking a Data Science engineer to work on a contract basis. The role involves designing, building, and deploying machine learning models and data pipelines to support scalable AI solutions. You will collaborate with cross-functional teams to translate business requirements into technical solutions.



Key Responsibilities:

• Develop and maintain production-grade data science models using Python and relevant frameworks.

• Design and implement data pipelines to process large-scale datasets for model training and inference.

• Collaborate with software engineers to integrate models into production systems and APIs.

• Optimize models for performance, scalability, and cost-efficiency in cloud environments.

• Conduct rigorous testing and validation to ensure model accuracy, reliability, and compliance.



Required Skills & Qualifications:

• Proficiency in Python with experience in data science libraries such as NumPy, Pandas, and Scikit-learn.

• Experience with machine learning frameworks including TensorFlow, PyTorch, or similar tools.

• Strong background in statistical modeling, regression, classification, and clustering techniques.

• Familiarity with cloud platforms (AWS, GCP, or Azure) and big data tools (Spark, Hadoop).

• Experience with SQL and database systems for data extraction and transformation.

• Ability to write clean, maintainable, and well-documented code.

• Understanding of MLOps practices, including model deployment and monitoring.

• Experience with version control systems such as Git.



More About the Opportunity:

This role offers a unique opportunity to work with a global leader in the Technology, Information and Internet industry, contributing to the development of cutting-edge AI solutions that drive business outcomes. You will have the opportunity to solve complex data challenges in a collaborative, remote-first environment.



Equal Opportunity Employer:

We hire based on skills and expertise. All qualified candidates are welcome regardless of background, experience, or prior employment history. Applications are reviewed solely on demonstrated technical ability and qualifications.

'''