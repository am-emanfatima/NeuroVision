"""Working contact workflows: SMTP send / email-client draft / .eml fallback."""
from __future__ import annotations
import streamlit as st
from contact_service import ContactMessage, ContactConfigurationError, make_eml, make_mailto, send_smtp, valid_email
from site_theme import page_intro, section

page_intro("Get in touch", "Questions? Let's talk research.",
 "For collaborations, reproducibility questions, project feedback or technical inquiries, use the contact form below. No contact address is invented or hard-coded into the app.")

try:
    config=dict(st.secrets.get("contact",{}))
except Exception:
    config={}  # A missing/invalid secrets file must not break public contact page.
recipient=str(config.get("recipient","")).strip()
smtp_enabled=all(config.get(k) for k in ("host","port","username","password","sender","recipient"))

left,right=st.columns([1.45,.85],gap="large")
with left:
    with st.form("contact_form",clear_on_submit=False):
        a,b=st.columns(2,gap="medium")
        with a: sender_name=st.text_input("Your name *",placeholder="Your name",max_chars=100)
        with b: sender_email=st.text_input("Your email *",placeholder="you@example.com",max_chars=254)
        subject=st.text_input("Subject *",placeholder="Research / collaboration inquiry",max_chars=140)
        message=st.text_area("Message *",placeholder="Share what you would like to discuss…",height=170,max_chars=3000)
        acknowledge=st.checkbox("I understand this contact channel is not for patient emergencies or confidential medical records.")
        submitted=st.form_submit_button("Prepare / send message",type="primary",use_container_width=True)
    if submitted:
        request=ContactMessage(sender_name.strip(),sender_email.strip(),subject.strip(),message.strip())
        try:
            from contact_service import verify_message
            verify_message(request)
            if not acknowledge:
                st.error("Please confirm the contact use notice above.")
            elif smtp_enabled:
                try:
                    send_smtp(request,config)
                    st.success("Message successfully sent to the configured project contact address.")
                except Exception:
                    st.error("The SMTP server did not confirm delivery. No message was saved by this application; you may use the email-client draft below.")
                    if valid_email(recipient):
                        st.link_button("Open email-client draft",make_mailto(recipient,request),use_container_width=True)
                    st.download_button("Download backup email draft (.eml)",make_eml(request,recipient),file_name="neurovision-contact.eml",mime="message/rfc822",use_container_width=True)
            elif valid_email(recipient):
                draft=make_mailto(recipient,request)
                st.success("Your message is ready. Open the email draft and send it from your email application.")
                st.link_button("Open email draft",draft,use_container_width=True)
                st.download_button("Download draft (.eml) instead",make_eml(request,recipient),file_name="neurovision-contact.eml",mime="message/rfc822",use_container_width=True)
                st.caption("Opening a draft does not send an email automatically.")
            else:
                st.info("This deployment has not set a contact recipient. Download the email draft and address it to your project's real contact manually.")
                st.download_button("Download email draft (.eml)",make_eml(request),file_name="neurovision-contact.eml",mime="message/rfc822",use_container_width=True)
        except (ValueError,ContactConfigurationError) as exc:
            st.error(str(exc))
with right:
    st.markdown("""<div class='nv-panel'><div class='nv-eyebrow'>Contact options</div>
    <h3 style='font-size:22px;color:#F1F9FF;margin:12px 0'>Project inquiries</h3>
    <p>Share feedback, report technical issues, discuss an academic demonstration, or ask about the methods used in this prototype.</p>
    <hr style='border-color:#304B60'>
    <p><b>Scope:</b> Research platform and engineering.</p>
    <p><b>Not for:</b> Personal health questions, urgent medical help, or medical decisions.</p></div>""",unsafe_allow_html=True)
    if smtp_enabled: st.success("Contact channel: SMTP configured")
    elif valid_email(recipient): st.info("Contact channel: email-client draft")
    else: st.warning("Contact channel: recipient not configured. Draft downloads remain available.")
    st.page_link("site_pages/about.py",label="About the platform",icon=":material/info:",use_container_width=True)

section("Frequently asked questions")
with st.expander("Can this platform give a diagnosis?"):
    st.write("No. The four scores describe model behavior on one uploaded image and are not validated medical probabilities. A qualified radiologist must assess a complete examination for clinical diagnosis.")
with st.expander("Can I download a patient-style PDF?"):
    st.write("Yes. The MRI Analysis page creates a formatted PDF with optional patient or study information. It is always clearly marked research-only, unsigned and non-diagnostic.")
with st.expander("Does the contact form really send messages?"):
    st.write("Yes, when the deployment owner supplies SMTP settings in Streamlit secrets. Otherwise the form opens an email-client draft if a recipient exists, or provides an .eml draft download. It never claims that an unsent draft was delivered.")
