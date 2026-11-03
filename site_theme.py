"""Design system and shared components for NeuroVision AI's research website."""
from __future__ import annotations
import html
import streamlit as st
from backend import APP_VERSION

COLOR = {"mint":"#4DE4C7", "blue":"#70ADFF", "violet":"#B99BFF", "peach":"#FFBA95"}

GLOBAL_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; }
html, body, [data-testid="stApp"], [class*="st-"] { font-family:'DM Sans', 'Segoe UI', sans-serif; }
.stApp {background: radial-gradient(ellipse at 0% 0%,rgba(33,75,125,.32),transparent 32%),radial-gradient(ellipse at 100% 17%,rgba(14,103,102,.20),transparent 32%),#090F1C;color:#EAF3FF; }
.block-container {max-width:1240px; padding-top:1.5rem; padding-bottom:4.2rem;}
[data-testid="stHeader"] {background:rgba(9,15,28,.94);border-bottom:1px solid #23334A;}
[data-testid="stToolbar"] {right:1rem;}
[data-testid="stDecoration"] {display:none;}
[data-testid="stSidebar"] {background:#0C1628;}
[data-testid="stMainMenu"] {color:#D6E8FF;}
[data-testid="stAlert"] {border-radius:13px;}
[data-testid="stFileUploader"] {border:1px solid #2B435B;border-radius:16px;padding:6px 10px;background:rgba(17,34,55,.60)}
[data-testid="stFileUploaderDropzone"] {background:rgba(29,57,76,.46);border:1px dashed #407F97;border-radius:13px;}
[data-testid="stImage"] img {border-radius:14px;border:1px solid #2D455C;}
[data-testid="stExpander"] {border:1px solid #28405B;border-radius:14px;background:rgba(16,31,51,.64);}
[data-testid="stMetric"] {padding:16px;background:rgba(17,34,54,.85);border-radius:13px;border:1px solid #293D56;}
[data-testid="stMetricValue"] {font-family:'Outfit',sans-serif;}
[data-testid="stDataFrame"] {border-radius:14px;overflow:hidden;}
[data-testid="stForm"] {padding:1.1rem 1.25rem;border:1px solid #2D435A;background:rgba(18,31,50,.85);border-radius:18px;}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:#2D425D!important;}
[data-testid="stVerticalBlockBorderWrapper"]>div {border-radius:16px!important;}
.stButton>button {font-family:'DM Sans',sans-serif;font-weight:700;border-radius:11px;min-height:47px;border:1px solid #3D5876;transition:box-shadow .2s ease,transform .2s ease;}
.stButton>button:hover,.stDownloadButton>button:hover {border-color:#64E7D4;box-shadow:0 0 0 2px rgba(64,231,212,.12);}
.stButton>button[kind="primary"]{background:linear-gradient(110deg,#57E5D0,#8DDFF6);color:#071C2E;border:0;font-weight:800;}
.stDownloadButton>button {background:rgba(19,45,67,.95);color:#DBF7FF;border:1px solid #40617D;border-radius:11px;min-height:45px;font-weight:700;}
.stPageLink a {border-radius:12px!important;background:rgba(25,50,73,.74);border:1px solid #31546B;padding:13px 16px!important;transition:all .2s;}
.stPageLink a:hover{background:rgba(33,78,89,.8);border-color:#46D6C3;}
.stTextInput input,.stTextArea textarea,.stDateInput input {background:rgba(9,20,35,.9);border-radius:11px;border:1px solid #35506C;}
.stTextInput input:focus,.stTextArea textarea:focus {border-color:#63DCCB!important;}
[data-testid="stWidgetLabel"] p {color:#BFCDE1;font-size:.91rem;}
a {color:#69D8DD;} a:hover{color:#95F0E6;}
hr {border-color:rgba(64,92,119,.65);}
h1,h2,h3,h4 {font-family:'Outfit','Segoe UI',sans-serif!important;letter-spacing:-.025em;font-weight:650;}
h1 {font-size:clamp(2.5rem,5vw,4rem)!important;line-height:1.12!important;}
h2 {font-size:clamp(1.8rem,3vw,2.25rem)!important;}
.nv-header {display:flex;justify-content:space-between;align-items:center;padding:4px 0 14px;border-bottom:1px solid rgba(83,110,134,.37);margin-bottom:24px;gap:14px}
.nv-brand{display:flex;align-items:center;gap:10px;font-family:'Outfit',sans-serif;font-size:19px;letter-spacing:-.4px;color:white;font-weight:800}
.nv-brand span{color:#5DEAD4}
.nv-logo{width:36px;height:36px;background:linear-gradient(135deg,#50DAC9,#749DF5);color:#061521;display:grid;place-items:center;border-radius:11px;font-weight:900;font-size:21px;box-shadow:0 4px 18px #0C9AA437}
.nv-header-note{font-size:11px;letter-spacing:.11em;font-weight:700;color:#91A9BC;text-transform:uppercase}
.nv-eyebrow{font-size:11px;font-weight:800;letter-spacing:.20em;text-transform:uppercase;color:#66E3D5;}
.nv-hero{border-radius:26px;border:1px solid #2A5769;background:linear-gradient(115deg,#102840 0%,#10334B 59%,#0D4149 100%);padding:46px 44px;box-shadow:0 20px 64px rgba(0,0,0,.20);position:relative;overflow:hidden;margin:2px 0 24px}
.nv-hero:before{content:'';position:absolute;right:-110px;top:-160px;width:550px;height:550px;background:radial-gradient(circle,#3AE7C21B,transparent 65%);pointer-events:none}
.nv-hero h1{font-size:clamp(2.6rem,5vw,4.1rem)!important;margin:17px 0 14px;color:#F5FBFF;max-width:790px;font-weight:750}
.nv-hero p{max-width:660px;color:#BBD1DE;line-height:1.7;font-size:16px;margin:0}
.nv-hero strong{color:#65E8D1}
.nv-hero-mini{margin-top:24px;display:flex;gap:15px;flex-wrap:wrap;font-size:12px;color:#B5CBD7}
.nv-hero-mini span{padding:9px 12px;border:1px solid #356075;border-radius:50px;background:#11334B}
.nv-title{font-size:30px;font-weight:750;color:#F3F8FF;line-height:1.22;margin:0 0 9px;font-family:'Outfit',sans-serif}
.nv-subtitle{color:#AFC1D5;font-size:15px;line-height:1.7;margin:0 0 20px;max-width:850px}
.nv-section{display:flex;justify-content:space-between;gap:12px;align-items:center;margin:32px 0 17px;font-family:'Outfit',sans-serif;font-size:25px;letter-spacing:-.025em;color:#F5F9FF;font-weight:700}
.nv-card{border:1px solid #2A4059;background:linear-gradient(150deg,rgba(19,37,61,.96),rgba(14,27,45,.94));border-radius:18px;padding:23px;min-height:175px;height:100%;}
.nv-card h3{font-size:20px;color:#F0F7FF;margin:15px 0 7px;font-weight:650;}
.nv-card p{margin:0;color:#A6BACF;font-size:13px;line-height:1.75}
.nv-card .nv-icon{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;background:#183D4F;color:#5BE7D3;font-size:21px;font-weight:700}
.nv-stat{border:1px solid #284359;background:rgba(15,31,52,.90);border-radius:16px;padding:18px 19px;margin:4px 0;}
.nv-stat .value{font-family:'Outfit',sans-serif;color:#F0FFFA;font-weight:750;font-size:29px;line-height:1.1}
.nv-stat .name{color:#8DA9BF;font-weight:650;text-transform:uppercase;letter-spacing:.10em;font-size:10px;margin-top:7px}
.nv-panel{border:1px solid #2C455F;border-radius:18px;background:rgba(18,35,55,.83);padding:23px;margin-bottom:12px;}
.nv-panel p{color:#ADBED0;line-height:1.7;font-size:14px;}
.nv-note{background:rgba(51,60,55,.41);border:1px solid #75654A;border-left:3px solid #EFBA6E;padding:15px 18px;border-radius:12px;color:#E5CFAD;font-size:13px;line-height:1.6;margin:11px 0 21px}
.nv-info{background:#102E43;border:1px solid #285A69;border-left:3px solid #50D7CD;padding:14px 18px;border-radius:12px;color:#C2E8F0;font-size:13px;line-height:1.65;margin:12px 0;}
.nv-tag{display:inline-flex;align-items:center;gap:8px;font-size:11px;font-weight:750;letter-spacing:.09em;padding:8px 12px;background:rgba(61,139,139,.13);border:1px solid rgba(74,200,190,.4);color:#72E8D8;border-radius:30px;text-transform:uppercase}
.nv-scorehero{background:linear-gradient(110deg,#143D51,#17464C);border:1px solid #297C7A;border-radius:19px;padding:25px 28px;margin:18px 0}
.nv-scorehero .label{font-size:11px;color:#97DAD6;text-transform:uppercase;font-weight:800;letter-spacing:.13em}
.nv-scorehero .answer{font-family:'Outfit',sans-serif;font-size:37px;font-weight:750;letter-spacing:-.02em;color:#ECFFF8;margin:8px 0}
.nv-scorehero .desc{color:#B3D3D9;font-size:13px;line-height:1.5}
.nv-fineprint{font-size:12px;color:#A5B5C7;line-height:1.7}
.nv-footer{border-top:1px solid #284055;margin-top:55px;padding:24px 0;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:11px;color:#8B9DB1}
.nv-footer b{color:#D0E4F0;}
.nv-visual{width:100%;max-width:560px;margin:auto;display:block;filter:drop-shadow(0 16px 32px rgba(0,0,0,.24))}
.nv-class{padding:20px;background:#101F33;border:1px solid #2A4057;border-radius:15px;min-height:127px}
.nv-class b{color:#E8F5FF;font-size:17px;font-family:'Outfit',sans-serif;}
.nv-class p{color:#9CB3C9;font-size:12px;margin:9px 0 0;line-height:1.6}
.nv-class .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:8px;}
@media(max-width:780px) {
.block-container{padding-top:.9rem;padding-left:1rem;padding-right:1rem;}
.nv-header{margin-bottom:13px;padding-bottom:11px;}
.nv-header-note{display:none}
.nv-hero{padding:30px 22px;border-radius:18px}
.nv-hero h1{font-size:2.65rem!important}
.nv-section{font-size:22px;margin-top:22px}
.nv-card{min-height:auto}
.nv-footer{margin-top:32px}
}
</style>
"""


def inject_theme() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def header() -> None:
    st.markdown("""<div class='nv-header'>
    <div class='nv-brand'><div class='nv-logo'>N</div><div>NeuroVision <span>AI</span></div></div>
    <div class='nv-header-note'>MRI Classification · Research Platform</div></div>""", unsafe_allow_html=True)


def footer() -> None:
    st.markdown(f"""<div class='nv-footer'>
      <div><b>NeuroVision AI</b> &nbsp;·&nbsp; Research platform v{html.escape(APP_VERSION)}</div>
      <div>Research use only &nbsp;·&nbsp; Non-diagnostic &nbsp;·&nbsp; No clinical sign-off</div>
    </div>""", unsafe_allow_html=True)


def section(name: str, eyebrow: str = "") -> None:
    kicker = f"<span class='nv-eyebrow'>{html.escape(eyebrow)}</span><br>" if eyebrow else ""
    st.markdown(f"<div class='nv-section'>{kicker}{html.escape(name)}</div>", unsafe_allow_html=True)


def card(icon: str, title: str, content: str) -> None:
    st.markdown(f"""<div class='nv-card'><div class='nv-icon'>{html.escape(icon)}</div>
    <h3>{html.escape(title)}</h3><p>{html.escape(content)}</p></div>""", unsafe_allow_html=True)


def page_intro(eyebrow: str, title: str, description: str) -> None:
    st.markdown(f"""<div class='nv-eyebrow'>{html.escape(eyebrow)}</div>
    <div class='nv-title' style='margin-top:10px'>{html.escape(title)}</div>
    <div class='nv-subtitle'>{html.escape(description)}</div>""", unsafe_allow_html=True)
