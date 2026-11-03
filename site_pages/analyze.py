"""Functional MRI research prediction and patient report workspace."""
from __future__ import annotations
from datetime import date
import hashlib
import html
import logging

import altair as alt
import pandas as pd
import streamlit as st

from backend import (
    AnalysisError, InferenceEngine, MAX_BYTES, RESEARCH_NOTICE,
    model_output_names, read_image_bytes, read_manifest,
)
from site_theme import page_intro, section
from web_reports import PatientDetails, export_csv, export_pdf

COLOR_BY_CLASS={"Glioma":"#70ADFF","Meningioma":"#B99BFF","No tumor":"#4DE4C7","Pituitary":"#FF9BAF"}

@st.cache_resource(show_spinner=False)
def get_engine() -> InferenceEngine:
    return InferenceEngine().load()


def reset_result() -> None:
    for key in ("mri_result","mri_result_hash"):
        st.session_state.pop(key,None)


def safe_age(value: str) -> str:
    if not value: return ""
    if value.isdigit() and 0<=int(value)<=120: return str(int(value))
    return ""


page_intro("Research workspace", "MRI image analysis",
   "Upload a brain MRI image, run the original bundled classifier, inspect four ranked model scores and download a structured research report. Predictions are generated live—not simulated.")
st.markdown("<div class='nv-note'><b>Research only · Not a medical diagnosis.</b> This application does not confirm or rule out tumors, and must not be used to guide treatment, screening or urgent care. The class-to-output order is configured but remains unverified against the training notebook.</div>",unsafe_allow_html=True)

try:
    labels,verified=model_output_names(read_manifest())
except AnalysisError:
    labels,verified=(),False
if labels:
    st.markdown("<span class='nv-tag'>4 class outputs</span> &nbsp; <span class='nv-tag'>EfficientNetB0</span> &nbsp; <span class='nv-tag'>JPEG / PNG</span>",unsafe_allow_html=True)

section("01 · Upload and validate")
left,right=st.columns([1.17,.83],gap="large")
with left:
    authorized=st.checkbox("I am authorized to process this image and understand the system is non-diagnostic.",key="image_authorization")
    file=st.file_uploader("Upload one MRI image", type=["png","jpg","jpeg"],disabled=not authorized,help="PNG or JPEG only, up to 30 MB. No DICOM or multi-series examinations.",key="mri_upload")
    decoded=None; metadata=None; contents=None; fingerprint=None
    if file and authorized:
        contents=file.getvalue()
        fingerprint=hashlib.sha256(contents).hexdigest()
        if st.session_state.get("mri_result_hash") != fingerprint:
            reset_result()
        try:
            decoded,metadata=read_image_bytes(contents,file.name)
            st.image(decoded,caption="Uploaded research image — no diagnostic interpretation",use_container_width=True)
        except AnalysisError as exc:
            st.error(str(exc))
    elif not authorized:
        reset_result()
with right:
    if metadata:
        st.markdown("""<div class='nv-panel' style='margin-top:8px'><div class='nv-eyebrow'>Image inspection</div><h3 style='font-size:22px;color:#F3FAFF;margin:10px 0'>Ready for inference</h3></div>""",unsafe_allow_html=True)
        m1,m2=st.columns(2)
        with m1:
            st.metric("Image width",f"{metadata.width} px")
            st.metric("File format",metadata.format)
        with m2:
            st.metric("Image height",f"{metadata.height} px")
            st.metric("File size",f"{metadata.bytes_count/1048576:.2f} MB")
        st.caption("In-memory processing · Input resized to 224 × 224 RGB. Uploaded image pixels are not placed in PDF unless you choose the appendix option.")
    else:
        st.markdown("""<div class='nv-panel' style='min-height:220px;margin-top:7px'>
        <div class='nv-eyebrow'>01 / Input readiness</div><h3 style='color:#F1F9FF;font-size:24px;margin:15px 0'>Your workspace awaits.</h3>
        <p>Authorize processing, then upload a JPEG or PNG image. Accepted images are previewed here before the model runs.</p>
        <div class='nv-info' style='margin-top:25px'>Supported: JPEG and PNG · Max 30 MB · Single image</div>
        </div>""",unsafe_allow_html=True)

section("02 · Patient & study metadata")
with st.expander("Add information for your optional PDF report",expanded=False):
    st.caption("Optional. For public demos, use a pseudonym / research code instead of identifiable patient information. These fields are included in the PDF—not the CSV.")
    aa,bb,cc=st.columns(3,gap="medium")
    with aa:
        patient_name=st.text_input("Patient name / pseudonym",key="patient_name",max_chars=120,placeholder="Research subject or alias")
        patient_id=st.text_input("Patient ID / study code",key="patient_id",max_chars=70,placeholder="Optional identifier")
    with bb:
        age_input=st.text_input("Age (years)",key="patient_age",max_chars=3,placeholder="Optional")
        sex=st.selectbox("Sex / gender (as recorded)",options=["Not provided","Female","Male","Other"],key="patient_sex")
    with cc:
        study_date=st.date_input("Study date",value=None,format="YYYY-MM-DD",key="patient_study_date")
        referred=st.text_input("Referring physician / service",max_chars=120,key="patient_referral")
    x,y=st.columns(2,gap="medium")
    with x:
        institution=st.text_input("Facility / research institution",max_chars=120,key="patient_facility")
        sequence=st.text_input("MRI sequence / view (if known)",max_chars=100,key="patient_sequence")
    with y:
        indication=st.text_area("Clinical indication (as entered by user)",max_chars=500,height=110,key="patient_indication")
    if age_input and not safe_age(age_input):
        st.warning("Age must be a whole number from 0 to 120. The PDF will omit an invalid age.")

# Widgets above exist even if the metadata expander is collapsed.
patient=PatientDetails(
    name=st.session_state.get("patient_name","").strip(),
    patient_id=st.session_state.get("patient_id","").strip(),
    age=safe_age(st.session_state.get("patient_age","")),
    sex="" if st.session_state.get("patient_sex","Not provided")=="Not provided" else st.session_state["patient_sex"],
    study_date=st.session_state.get("patient_study_date").isoformat() if st.session_state.get("patient_study_date") else "",
    referring_clinician=st.session_state.get("patient_referral","").strip(),
    institution=st.session_state.get("patient_facility","").strip(),
    sequence=st.session_state.get("patient_sequence","").strip(),
    clinical_indication=st.session_state.get("patient_indication","").strip(),
)

section("03 · Compute model prediction")
submit=st.button("Analyze uploaded MRI", type="primary",use_container_width=True,disabled=(not authorized or decoded is None),key="submit_prediction")
if submit and decoded is not None and metadata is not None and fingerprint is not None:
    try:
        with st.spinner("Loading the bundled model and calculating genuine output scores…"):
            prediction=get_engine().analyze(decoded,metadata)
        st.session_state["mri_result"]=prediction
        st.session_state["mri_result_hash"]=fingerprint
    except (AnalysisError,ValueError,OSError) as exc:
        reset_result()
        st.error(str(exc))
    except Exception:
        reset_result()
        logging.exception("Inference failed")
        st.error("The model could not run on this server. Verify TensorFlow compatibility and review the deployment logs.")

result=st.session_state.get("mri_result")
if result is not None and authorized and fingerprint and st.session_state.get("mri_result_hash")==fingerprint:
    section("04 · Classification results")
    name=result.output_names[result.primary_index]
    st.markdown(f"""<div class='nv-scorehero'>
    <div class='label'>Highest-scoring configured class</div>
    <div class='answer'>{html.escape(name)}</div>
    <div class='desc'>Model score: <b>{result.top_score:.2f}%</b> &nbsp;·&nbsp; Score gap to next class: <b>{result.margin:.2f} percentage points</b>. These are <b>not</b> calibrated clinical probabilities.</div>
    </div>""",unsafe_allow_html=True)
    if result.labels_verified:
        st.success("Class names are verified against training metadata.")
    else:
        st.warning("Class names are configured from the app manifest. The training class-index order has not been independently verified; the labels may be assigned to incorrect model outputs.")

    scores=[{"Class":result.output_names[i],"Score (%)":round(result.scores[i]*100,4),"Color":COLOR_BY_CLASS.get(result.output_names[i],"#6F8FAF")} for i in range(4)]
    scores.sort(key=lambda s:s["Score (%)"],reverse=True)
    df=pd.DataFrame(scores)
    chart=alt.Chart(df).mark_bar(cornerRadiusTopRight=5,cornerRadiusBottomRight=5,size=27).encode(
        x=alt.X("Score (%):Q",scale=alt.Scale(domain=[0,100]),axis=alt.Axis(title="Model score (%)",grid=True,gridColor="#29405A",labelColor="#B4C8DA",titleColor="#D5E8F4")),
        y=alt.Y("Class:N",sort=alt.SortField(field="Score (%)",order="descending"),axis=alt.Axis(title=None,labelColor="#DDEEFF",labelFontSize=13)),
        color=alt.Color("Color:N",scale=None,legend=None),
        tooltip=[alt.Tooltip("Class:N"),alt.Tooltip("Score (%):Q",format=".2f")],
    ).properties(height=270).configure_view(strokeWidth=0).configure(background="transparent")
    st.altair_chart(chart,use_container_width=True)
    st.markdown("**Detailed class ranking**")
    rank_df=pd.DataFrame({"Rank":list(range(1,5)),"Class":[a["Class"] for a in scores],"Model score (%)":[round(a["Score (%)"],2) for a in scores]})
    st.dataframe(rank_df,hide_index=True,use_container_width=True)
    st.markdown(f"""<div class='nv-info'><b>Interpretation:</b> The leading configured label is <b>{html.escape(name)}</b>. The second-ranked label is <b>{html.escape(result.output_names[result.secondary_index])}</b>. This describes only the current network output; it does not confirm or exclude a medical condition.</div>""",unsafe_allow_html=True)

    section("05 · Download the analysis")
    include_image=st.checkbox("Include uploaded image in PDF appendix",value=False,key="pdf_include_image")
    st.caption("The PDF contains optional patient metadata and is always unsigned and explicitly non-diagnostic. The CSV contains model output values only.")
    a,b=st.columns(2,gap="medium")
    with a:
        try:
            report=export_pdf(result,patient,image_bytes=contents if include_image else None)
            st.download_button("Download patient-style research PDF",data=report,file_name="NeuroVisionAI_MRI_Research_Report.pdf",mime="application/pdf",use_container_width=True,type="primary")
        except Exception:
            logging.exception("PDF generation error")
            st.error("The PDF could not be created. Try again without the image appendix.")
    with b:
        st.download_button("Download class scores CSV",data=export_csv(result),file_name="NeuroVisionAI_Class_Scores.csv",mime="text/csv",use_container_width=True)
    st.markdown(f"<p class='nv-fineprint'>{html.escape(RESEARCH_NOTICE)}</p>",unsafe_allow_html=True)
else:
    st.markdown("<div class='nv-info'>Results will appear here after you provide a valid image, consent to its processing and run the model.</div>",unsafe_allow_html=True)
