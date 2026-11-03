"""Safe optional SMTP delivery and honest email-client fallback."""
from __future__ import annotations
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import parseaddr
import re
import smtplib
from urllib.parse import quote

class ContactConfigurationError(RuntimeError):
    pass

@dataclass(frozen=True)
class ContactMessage:
    sender_name: str
    sender_email: str
    subject: str
    body: str


def valid_email(value: str) -> bool:
    if not value or len(value)>254 or any(c in value for c in '\r\n\t'):
        return False
    display,address=parseaddr(value)
    if address!=value.strip() or display:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?\.[A-Za-z]{2,}",address))


def verify_message(msg: ContactMessage) -> None:
    # Disallow control characters in values that may enter email headers.
    if any(ord(c)<32 or ord(c)==127 for c in (msg.sender_name + msg.subject)):
        raise ValueError("Name and subject cannot contain line breaks or control characters.")
    if not 2<=len(msg.sender_name.strip())<=100:
        raise ValueError("Enter a name of 2–100 characters.")
    if not valid_email(msg.sender_email):
        raise ValueError("Enter a valid reply email address.")
    if not 3<=len(msg.subject.strip())<=140:
        raise ValueError("Enter a subject of 3–140 characters.")
    if not 10<=len(msg.body.strip())<=3000:
        raise ValueError("Enter a message of 10–3000 characters.")


def make_mailto(recipient: str, msg: ContactMessage) -> str:
    verify_message(msg)
    if not valid_email(recipient):
        raise ContactConfigurationError("Contact email address is not configured correctly.")
    text=f"From: {msg.sender_name}\nReply email: {msg.sender_email}\n\n{msg.body}"
    return f"mailto:{recipient}?subject={quote(msg.subject)}&body={quote(text)}"


def make_eml(msg: ContactMessage, recipient: str = "") -> bytes:
    verify_message(msg)
    email=EmailMessage()
    email["From"]=msg.sender_email
    if recipient and valid_email(recipient): email["To"]=recipient
    email["Subject"]=msg.subject
    email.set_content(f"Sender: {msg.sender_name}\nReply address: {msg.sender_email}\n\n{msg.body}")
    return email.as_bytes()


def send_smtp(msg: ContactMessage, cfg: dict) -> None:
    """Deliver with TLS; no emails are stored on disk by this source code."""
    verify_message(msg)
    required=("host","port","username","password","recipient","sender")
    if not all(cfg.get(k) for k in required):
        raise ContactConfigurationError("SMTP is not completely configured.")
    if not (valid_email(str(cfg["sender"])) and valid_email(str(cfg["recipient"]))):
        raise ContactConfigurationError("Invalid sender or recipient address in SMTP configuration.")
    try:
        port=int(cfg["port"])
    except (ValueError,TypeError):
        raise ContactConfigurationError("Invalid SMTP port.")
    if not 1<=port<=65535:
        raise ContactConfigurationError("Invalid SMTP port.")
    email=EmailMessage()
    email["From"]=str(cfg["sender"])
    email["To"]=str(cfg["recipient"])
    email["Reply-To"]=msg.sender_email
    email["Subject"]="NeuroVision AI: "+msg.subject
    email.set_content(f"Sender name: {msg.sender_name}\nReply address: {msg.sender_email}\n\n{msg.body}")
    timeout=12
    if bool(cfg.get("use_ssl",False)):
        with smtplib.SMTP_SSL(str(cfg["host"]),port,timeout=timeout) as client:
            client.login(str(cfg["username"]),str(cfg["password"]))
            client.send_message(email)
    else:
        with smtplib.SMTP(str(cfg["host"]),port,timeout=timeout) as client:
            client.ehlo()
            client.starttls()
            client.ehlo()
            client.login(str(cfg["username"]),str(cfg["password"]))
            client.send_message(email)
