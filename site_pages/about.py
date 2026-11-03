"""Model provenance, methodological transparency and scope."""
from __future__ import annotations
import streamlit as st
from site_theme import card, page_intro, section
from backend import MODEL_PATH, model_output_names, read_manifest, AnalysisError

page_intro("The platform", "Built for research. Grounded in transparency.",
    "NeuroVision AI is a self-contained educational research interface built around a user-supplied EfficientNetB0 brain MRI image classifier. The design brings together model inference, transparent score visualization and report generation.")

section("What powers the platform")
c1,c2,c3 = st.columns(3,gap="medium")
with c1: card("AI","EfficientNetB0","A bundled Keras model performs four-class softmax inference on a single RGB image.")
with c2: card("224","Image pipeline","Validated JPEG/PNG files are converted to RGB and resized to 224 × 224 for prediction.")
with c3: card("PDF","Research reporting","ReportLab creates an unsigned patient-style research PDF; a CSV download preserves the raw class score values.")

section("Model information")
try:
    manifest=read_manifest()
    names,verified=model_output_names(manifest)
    status="Verified against training records" if verified else "Configured—training class index not independently verified"
    data={
      "Model file":MODEL_PATH.name,
      "Network":"EfficientNetB0-based image classifier",
      "Input":"224 × 224 pixels · RGB · float32",
      "Output":"4-way softmax normalized class scores",
      "Configured class names":" · ".join(names),
      "Class label status":status,
      "Model checksum (SHA-256)":manifest.get("sha256", "Unavailable"),
    }
    for k,v in data.items():
        a,b=st.columns([1,2.4],gap="medium")
        with a: st.markdown(f"**{k}**")
        with b: st.write(v)
        st.divider()
except AnalysisError:
    st.warning("The model manifest could not be read on this deployment.")

section("How the analysis works")
for num,title,desc in [
 ("01","Validate upload","Reject invalid image formats, excessively large files and images too small for the pipeline."),
 ("02","Preprocess for inference","Convert to RGB, apply EXIF orientation, resize to 224 × 224 and provide float32 pixel values to the saved network."),
 ("03","Compute model scores","The real Keras model produces four normalized output values. Scores are ranked and plotted without fabricating findings."),
 ("04","Generate a research record","Optional patient metadata and outputs are formatted in a structured PDF marked non-diagnostic; raw scores can be exported as CSV."),
]:
    st.markdown(f"""<div class='nv-panel' style='margin-bottom:10px;min-height:80px'><span class='nv-eyebrow'>Step {num}</span>
    <h3 style='font-size:21px;color:#F4F9FF;margin:8px 0 5px'>{title}</h3><p style='margin:0'>{desc}</p></div>""",unsafe_allow_html=True)

section("What this tool does not do")
st.markdown("""<div class='nv-note'>
<b>Not clinically validated.</b> This app does not diagnose, rule out, stage or monitor brain tumors, and should not be used for screening, triage, treatment or other patient-care decisions.
It does not accept DICOM series, reconstruct 3D scans, provide segmentation, or replace formal radiological reporting.
</div>""",unsafe_allow_html=True)
st.markdown("""The class names **Glioma**, **Meningioma**, **No tumor** and **Pituitary** are configured according to the application's BRISC2025 manifest. The training notebook's actual class-to-output mapping has not been provided, so no claim of verified alignment is made. Independently evaluate dataset provenance, intended use, bias, performance and external generalization before a research publication or demonstration.""")
st.page_link("site_pages/analyze.py",label="Go to MRI Analysis",icon=":material/arrow_forward:",use_container_width=True)
