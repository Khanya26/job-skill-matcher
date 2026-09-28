import pandas as pd
import requests
import streamlit as st

from matcher import (
    analyze_match,
    extract_pdf_text,
    get_ai_recommendations,
)



# PAGE CONFIG


st.set_page_config(
    page_title="SkillMatch AI",
    layout="wide",
    initial_sidebar_state="expanded",
)



# CUSTOM CSS


st.markdown(
    """
<style>

.stApp {
    background-color: #f6f8fb;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

[data-testid="stSidebar"] * {
    color: white;
}

.hero-box {
    padding: 2.5rem;
    border-radius: 18px;
    background-color: #111827;
    margin-bottom: 2rem;
}

.hero-badge {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #d1d5db;
    margin-bottom: 0.8rem;
}

.hero-title {
    font-size: 2.7rem;
    font-weight: 750;
    color: white;
    margin-bottom: 0.6rem;
}

.hero-text {
    font-size: 1rem;
    color: #d1d5db;
    max-width: 720px;
    line-height: 1.6;
}

.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #111827;
    margin-top: 1.5rem;
}

.section-text {
    color: #6b7280;
    margin-bottom: 1rem;
}

.card {
    background-color: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1.3rem;
    margin-bottom: 1rem;
}

.card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #111827;
}

.card-text {
    color: #6b7280;
    font-size: 0.85rem;
}

.skill {
    display: inline-block;
    padding: 0.35rem 0.7rem;
    margin: 0.2rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
}

.skill-match {
    background-color: #f0fdf4;
    color: #166534;
    border: 1px solid #bbf7d0;
}

.skill-missing {
    background-color: #fff7ed;
    color: #9a3412;
    border: 1px solid #fed7aa;
}

.evidence {
    background-color: white;
    border-left: 4px solid #111827;
    padding: 1rem;
    margin-bottom: 0.7rem;
    border-radius: 8px;
}

.privacy {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1.3rem;
    margin-top: 2rem;
}

.footer {
    text-align: center;
    color: #9ca3af;
    font-size: 0.8rem;
    margin-top: 2rem;
}

</style>
""",
    unsafe_allow_html=True,
)


# SIDEBAR


with st.sidebar:

    st.title(" SkillMatch AI")

    st.caption(
        "Explainable resume-to-job matching"
    )

    st.divider()

    st.subheader("How it works")

    st.write("01 · Upload or paste resume")
    st.write("02 · Add job description")
    st.write("03 · Analyze skill match")
    st.write("04 · Review evidence")
    st.write("05 · Get AI suggestions")

    st.divider()

    st.subheader("Technology")

    st.write(" Python")
    st.write(" Streamlit")
    st.write(" TF-IDF / scikit-learn")
    st.write(" OpenRouter AI")

    st.divider()

    st.caption(
        "AI coaching is optional. "
        "The local matching report remains "
        "the scoring authority."
    )



# HERO


st.markdown(
    """
<div class="hero-box">

<div class="hero-badge">
AI-POWERED · EXPLAINABLE · PRIVACY-AWARE
</div>

<div class="hero-title">
Find the skills that connect you to the job.
</div>

<div class="hero-text">
Compare a resume with a job description using
explainable NLP, skill matching, and optional
AI-powered improvement suggestions.
</div>

</div>
""",
    unsafe_allow_html=True,
)



# SAMPLE DATA


SAMPLE_RESUME = """Data Analyst

Built ML pipelines in Python and pandas to forecast product demand.
Created SQL reports and automated weekly data-quality checks.
Deployed an internal Streamlit dashboard for operations teams.
Used Git and Docker to package and review analytics work.
"""


SAMPLE_JOB_DESCRIPTION = """We are hiring a Junior Machine Learning Engineer.

The role requires Python, machine learning, pandas, scikit-learn, SQL,
Streamlit, and AWS.

The candidate should communicate analytical findings and improve
repeatable data workflows.
"""



# INPUT SECTION


st.markdown(
    '<div class="section-title">Analyze your application</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-text">'
    "Provide your resume and the job description you want to evaluate."
    "</div>",
    unsafe_allow_html=True,
)


resume_col, job_col = st.columns(
    2,
    gap="large",
)



# RESUME


with resume_col:

    st.subheader(" Resume")

    st.caption(
        "Upload a text-based PDF or use the sample resume."
    )

    uploaded_file = st.file_uploader(
        "Upload resume PDF",
        type="pdf",
        max_upload_size=5,
    )

    resume_fallback = st.text_area(
        "Resume text",
        value=SAMPLE_RESUME,
        height=230,
        help="Used when no PDF is uploaded.",
    )

    pdf_text = None

    if uploaded_file is not None:

        try:

            pdf_text = extract_pdf_text(
                uploaded_file
            )

        except (ValueError, OSError) as exc:

            st.error(str(exc))

        else:

            st.success(
                f"PDF ready · {len(pdf_text):,} characters extracted"
            )



# JOB DESCRIPTION


with job_col:

    st.subheader(" Job description")

    st.caption(
        "Paste the requirements for the role you are targeting."
    )

    job_description = st.text_area(
        "Job description",
        value=SAMPLE_JOB_DESCRIPTION,
        height=230,
    )



# ANALYZE BUTTON


st.write("")

analyze_clicked = st.button(
    " Analyze Match",
    type="primary",
    width="stretch",
)


st.caption(
    "The deterministic matching report is generated locally. "
    "AI coaching is optional."
)



# ANALYSIS


if analyze_clicked:

    resume_text = (
        pdf_text
        if uploaded_file is not None
        else resume_fallback
    )

    if not resume_text or not resume_text.strip():

        st.error(
            "Please provide resume text or upload a readable PDF."
        )

    elif not job_description.strip():

        st.error(
            "Please provide a job description before analyzing."
        )

    else:

        with st.spinner(
            "Analyzing your application..."
        ):

            result = analyze_match(
                resume_text,
                job_description,
            )

        
        # SCORE SECTION
        

        st.markdown(
            '<div class="section-title">Match analysis</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-text">'
            "A transparent breakdown of similarity and required skills."
            "</div>",
            unsafe_allow_html=True,
        )

        score1, score2, score3, score4 = st.columns(4)

        with score1:

            st.metric(
                "Overall match",
                f"{result['overall_score']}%",
            )

        with score2:

            st.metric(
                "Skill coverage",
                f"{result['skill_coverage']}%",
            )

        with score3:

            st.metric(
                "Alias-aware",
                f"{result['alias_similarity']}%",
            )

        with score4:

            st.metric(
                "Lexical similarity",
                f"{result['lexical_similarity']}%",
            )

        st.info(
            "The overall score is a project-defined blend of "
            "alias-aware similarity and skill coverage. "
            "It is not a standardized hiring score."
        )

        # SKILLS BREAKDOWN
       

        st.markdown(
            '<div class="section-title">Skills breakdown</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-text">'
            "See which requirements were identified in the resume."
            "</div>",
            unsafe_allow_html=True,
        )

        if result["category_rows"]:

            st.dataframe(
                pd.DataFrame(
                    result["category_rows"]
                ),
                hide_index=True,
                width="stretch",
            )

        else:

            st.warning(
                "No skills from the current skill taxonomy "
                "were found in the job description."
            )
       
        # MATCHED / MISSING
        

        matched_col, missing_col = st.columns(
            2,
            gap="large",
        )

        with matched_col:

            st.subheader(" Matched skills")

            if result["matched_skills"]:

                for skill in result["matched_skills"]:

                    st.markdown(
                        f"""
                        <div style="
                            padding: 0.65rem 0;
                            font-size: 1rem;
                            color: #111827;
                        ">
                            <span style="
                                color: #16a34a;
                                font-weight: 700;
                                margin-right: 0.5rem;
                            ">✓</span>
                            {skill}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            else:

                st.caption(
                    "No matched skills identified."
                )


        with missing_col:

            st.subheader(" Skills to strengthen")

            if result["missing_skills"]:

                for skill in result["missing_skills"]:

                    st.markdown(
                        f"""
                        <div style="
                            padding: 0.65rem 0;
                            font-size: 1rem;
                            color: #111827;
                        ">
                            <span style="
                                color: #374151;
                                font-weight: 700;
                                margin-right: 0.8rem;
                            ">•</span>
                            {skill}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            else:

                st.caption(
                    "No missing skills identified."
                )
      
        # EVIDENCE
        

        st.markdown(
            '<div class="section-title">Supporting evidence</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-text">'
            "Resume sentences that support the matched skills."
            "</div>",
            unsafe_allow_html=True,
        )

        with st.expander(
            "View resume evidence",
            expanded=True,
        ):

            if result["evidence"]:

                for sentence in result["evidence"]:

                    st.markdown(
                        f"""
<div class="evidence">
{sentence}
</div>
""",
                        unsafe_allow_html=True,
                    )

            else:

                st.write(
                    "No supporting evidence sentence matched "
                    "the current skill taxonomy."
                )

        
        # AI COACH
        

        st.markdown(
            '<div class="section-title"> AI career coach</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-text">'
            "Optional suggestions based only on your match signals."
            "</div>",
            unsafe_allow_html=True,
        )

        st.info(
            "OpenRouter receives match scores and skill names, "
            "not your raw resume or job-description text."
        )

        try:

            api_key = st.secrets[
                "OPENROUTER_API_KEY"
            ]

        except (
            FileNotFoundError,
            KeyError,
        ):

            api_key = ""

        if not api_key or api_key == "your-api-key-here":

            st.warning(
                "AI coaching is unavailable because "
                "OPENROUTER_API_KEY has not been configured."
            )

        else:

            try:

                recommendations, model_used = (
                    get_ai_recommendations(
                        api_key,
                        result,
                    )
                )

            except requests.RequestException as exc:

                st.error(
                    f"OpenRouter request failed: {exc}"
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ) as exc:

                st.error(
                    f"OpenRouter returned an unexpected response: {exc}"
                )

            else:

                st.markdown(
                    recommendations
                )

                st.caption(
                    f"AI model: {model_used}"
                )

                st.warning(
                    "Verify every AI suggestion before editing "
                    "your resume. The model has not seen your raw "
                    "experience and must not be used to invent claims."
                )


# PRIVACY


st.markdown(
    """
<div class="privacy">

<strong> Privacy-aware matching</strong>

<br><br>

Resume and job-description text are used by the application
to generate the deterministic match report. Optional AI coaching
receives only match scores and skill names rather than the raw
resume or job-description text.

</div>
""",
    unsafe_allow_html=True,
)



# FOOTER

st.markdown(
    """
<div class="footer">
SkillMatch AI · Explainable Resume-to-Job Matching
</div>
""",
    unsafe_allow_html=True,
)