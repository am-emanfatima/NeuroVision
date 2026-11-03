"""Privacy and ethics page describing deployed prototype behavior precisely."""
from __future__ import annotations
import streamlit as st
from site_theme import page_intro, section

page_intro("Trust and safeguards","Privacy & responsible AI use",
   "A research demo should be clear about its limits, the data it handles and the safeguards needed before processing real patient material.")
section("Data handling in the supplied source code")
for title,body in [
("Image uploads","Uploaded image bytes are read in memory for inference on the server hosting Streamlit. This code does not intentionally persist uploaded images to a local database or permanent image folder. Hosting infrastructure may still process or log associated metadata."),
("Patient metadata","Optional patient/study fields live in the Streamlit app session and are inserted into the downloadable PDF. These fields are not inserted into the CSV. Treat any public deployment as a third-party server, not a secure hospital information system."),
("Report exports","PDF and CSV files are generated in memory when requested. An image is included in a PDF appendix only if you explicitly select that option."),
("Contact submissions","If SMTP is configured, the contact form sends entered content to the configured recipient over SMTP TLS/SSL. Otherwise, with a contact address configured, it opens an email-client draft; without contact settings, it offers a draft download. The app does not claim delivery without an active SMTP configuration."),
("Cookies and hosting","Streamlit and the deployment platform may use session state, cookies and logs. This demo does not implement a clinical-grade consent, authentication, retention, encryption-at-rest or access-control system."),
]:
    st.markdown(f"<div class='nv-panel'><h3 style='color:#F2FBFF;font-size:19px;margin:0 0 7px'>{title}</h3><p style='margin:0'>{body}</p></div>",unsafe_allow_html=True)
section("Use guidelines")
st.markdown("""1. Upload only images and details you have authorization to process; prefer de-identified research samples.
2. Do not use public demo hosting for identifiable patient information without an approved legal, privacy and information-security framework.
3. Do not interpret the four algorithmic scores as calibrated disease probabilities or a clinical finding.
4. Verify the training class-index mapping, model validation metrics, and external validity before making publication claims.
5. Obtain clinician review of the complete examination for any clinical concerns.""")
st.markdown("<div class='nv-note'><b>Medical disclaimer:</b> All reports from this application are unsigned, non-diagnostic educational records; they are not medical records authenticated by a physician.</div>",unsafe_allow_html=True)
st.page_link("site_pages/contact.py",label="Contact the project team",icon=":material/mail:",use_container_width=True)
