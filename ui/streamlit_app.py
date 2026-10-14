"""Streamlit client for the Resume Parser API."""

import os

import requests
import streamlit as st


API_URL = os.getenv("RESUME_API_URL", "http://127.0.0.1:8000")


def response_detail(response: requests.Response | None, fallback: str) -> str:
    """Return a useful error for JSON, text, empty, or proxy-generated responses."""

    if response is None:
        return fallback
    try:
        payload = response.json()
    except ValueError:
        body = response.text.strip()
        return body[:500] if body else f"API returned HTTP {response.status_code}."
    if isinstance(payload, dict):
        return str(payload.get("detail") or payload.get("message") or payload)
    return str(payload)


st.set_page_config(page_title="Resume Parser", page_icon="📄", layout="wide")
st.title("Resume Parser")
st.caption("Upload a PDF or DOCX resume to extract structured information.")

uploaded = st.file_uploader("Resume file", type=["pdf", "docx"])
if uploaded and st.button("Extract resume", type="primary"):
    with st.spinner("Extracting resume information..."):
        try:
            response = requests.post(
                f"{API_URL}/api/upload",
                files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)},
                timeout=120,
            )
            response.raise_for_status()
            st.session_state["resume"] = response.json()
        except requests.RequestException as exc:
            st.error(f"Could not parse resume: {response_detail(exc.response, str(exc))}")
        except ValueError:
            st.error("Could not parse resume: the API returned an invalid response.")

resume = st.session_state.get("resume")
if resume:
    st.success(f"Parsed {resume['filename']} (ID: {resume['document_id']})")
    contact = resume["contact_information"]
    st.subheader("Contact information")
    st.json(contact)
    st.subheader("Professional summary")
    st.write(resume.get("professional_summary") or "Not provided")
    left, right = st.columns(2)
    with left:
        st.subheader("Work experience")
        for item in resume["work_experience"]:
            st.markdown(f"**{item['role']} - {item['company']}**  \n{item.get('duration') or ''}")
            for responsibility in item["responsibilities"]:
                st.markdown(f"- {responsibility}")
        st.subheader("Education")
        for item in resume["education"]:
            st.markdown(f"**{item['degree']}**, {item['institution']} ({item.get('year') or 'year unavailable'})")
    with right:
        st.subheader("Technical skills")
        st.write(", ".join(resume["technical_skills"]) or "Not provided")
        st.subheader("Soft skills")
        st.write(", ".join(resume["soft_skills"]) or "Not provided")
        st.subheader("Certifications")
        st.write("\n".join(f"- {item}" for item in resume["certifications"]) or "Not provided")

