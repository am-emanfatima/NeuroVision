"""Public-facing homepage with clear research-only positioning."""
from __future__ import annotations
import streamlit as st
from site_theme import card, section

left_hero,right_hero=st.columns([1.18,.82],gap="medium")
with left_hero:
    st.markdown("""
    <div class='nv-hero'>
      <span class='nv-tag'>✦ &nbsp; Intelligent MRI research workspace</span>
      <h1>Explore brain MRI<br><strong>with clarity.</strong></h1>
      <p>Transform a single image into a transparent four-class model score profile. See the methodology and export a traceable research report.</p>
      <div class='nv-hero-mini'><span>✓ Original EfficientNetB0 model</span><span>✓ PDF &amp; CSV export</span></div>
    </div>""",unsafe_allow_html=True)
with right_hero:
    st.image("assets/hero_visual.png",use_container_width=True)
    st.caption("Original illustrative neural graphic — not a patient MRI image.")

a,b,c = st.columns([1.04,.98,1.15],gap="small")
with a: st.page_link("site_pages/analyze.py", label="Launch MRI analysis", icon=":material/arrow_forward:", use_container_width=True)
with b: st.page_link("site_pages/about.py", label="Explore the research", icon=":material/biotech:", use_container_width=True)
with c: st.caption("**Research / educational use only.** Outputs are not clinical diagnoses.")

section("A straightforward research workflow")
x,y,z = st.columns(3,gap="medium")
with x: card("01", "Upload an image", "Choose a JPEG or PNG MRI image. The app checks image format, size and dimensions before analysis.")
with y: card("02", "Inspect real model outputs", "Run the bundled EfficientNetB0 model and compare four ranked class scores in a transparent visualization.")
with z: card("03", "Export your research", "Generate a professional, unsigned research PDF with optional patient metadata, or download raw model scores as CSV.")

section("At a glance")
a,b,c,d = st.columns(4,gap="medium")
for col,number,caption in [(a,"4","research classes"),(b,"224²","RGB input pixels"),(c,"2","export formats"),(d,"1","image per analysis")]:
    with col:
        st.markdown(f"<div class='nv-stat'><div class='value'>{number}</div><div class='name'>{caption}</div></div>",unsafe_allow_html=True)

section("Four configured classes")
st.markdown("<p class='nv-subtitle'>The interface displays the following four BRISC2025 category names. Output-to-name alignment is configured but remains unconfirmed until the training class-index record is provided.</p>",unsafe_allow_html=True)
info=[("#70ADFF","Glioma","One of the four configured dataset categories."),
      ("#B99BFF","Meningioma","Displayed as a separate classifier category."),
      ("#4DE4C7","No tumor","A model label—not a clinical exclusion of disease."),
      ("#FF9BAF","Pituitary","The fourth configured image category.")]
columns=st.columns(4,gap="medium")
for col,(color,name,desc) in zip(columns,info):
    with col: st.markdown(f"<div class='nv-class'><b><span class='dot' style='background:{color}'></span>{name}</b><p>{desc}</p></div>",unsafe_allow_html=True)

section("Designed for responsible research")
left,right=st.columns([1.1,.9],gap="large")
with left:
    st.markdown("""<div class='nv-panel'><div class='nv-eyebrow'>Transparent by design</div>
        <h3 style='font-family:Outfit;font-size:25px;color:#F4F9FE;margin:13px 0'>A polished experience without overclaiming.</h3>
        <p>Predictions come from the supplied trained model—not mock data. Scores are explicitly described as algorithmic model outputs, not clinical confidence levels. The output class mapping is flagged as provisional until training metadata verifies it.</p>
        <p>The structured PDF supports research documentation and is clearly marked <b>unsigned</b> and <b>non-diagnostic</b>.</p>
        </div>""",unsafe_allow_html=True)
    st.page_link("site_pages/privacy.py",label="Read privacy & ethical use",icon=":material/security:",use_container_width=True)
with right:
    st.markdown("""<div class='nv-panel' style='min-height:252px'>
    <div class='nv-eyebrow'>Research disclosure</div>
    <div style='font-family:Outfit;font-size:46px;font-weight:750;color:#5AE1D1;margin:20px 0 4px'>AI ≠ diagnosis</div>
    <p>The system does not inspect a complete MRI exam, clinical history, or radiological sequences. A licensed radiologist is required for diagnostic interpretation.</p>
    </div>""",unsafe_allow_html=True)

st.markdown("<div class='nv-info'><b>Before uploading:</b> Only upload files that you are authorized to process. Avoid identifiable patient images or details on public hosting without an appropriate privacy, security and institutional approval process.</div>",unsafe_allow_html=True)
