"""Shared visual theme. Banner is the uploaded Rwanda photo (assets/banner.webp), darkened
with a CSS overlay for text contrast - no pixel editing needed, no external image fetch at
runtime (the file ships with the app).
"""
import base64
from pathlib import Path

import streamlit as st

BLUE, GREEN, RED = "#0057B8", "#1B4D3E", "#C0392B"
ASSETS = Path(__file__).resolve().parent / "assets"


def inject_theme():
    banner_b64 = base64.b64encode((ASSETS / "banner.webp").read_bytes()).decode()
    st.markdown(f"""
    <style>
      .hero {{
        background-image: linear-gradient(rgba(10,20,20,0.50), rgba(10,20,20,0.50)),
                           url("data:image/webp;base64,{banner_b64}");
        background-size: cover; background-position: center 35%;
        border-radius: 12px; padding: 30px 32px; margin-bottom: 14px; color: white;
        min-height: 150px; display: flex; flex-direction: column; justify-content: center;
      }}
      .hero h1 {{ margin: 0 0 4px 0; font-size: 1.8rem; font-weight: 700;
                  text-shadow: 0 1px 6px rgba(0,0,0,0.4); }}
      .hero p {{ margin: 0; font-size: 0.95rem; text-shadow: 0 1px 6px rgba(0,0,0,0.4); }}

      .finding-strip {{
        background: {GREEN}; color: white; border-radius: 10px; padding: 14px 20px;
        margin-bottom: 16px; font-size: 0.95rem; line-height: 1.5;
      }}
      .finding-strip b {{ font-size: 1.05rem; }}

      div[data-testid="stMetric"] {{
        background: #fafafa; border: 1px solid #ececec; border-radius: 10px; padding: 10px 14px;
      }}
      [data-testid="stMetricValue"] {{ color: {GREEN}; }}
      [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {{ color: #444 !important; }}
      [data-testid="stMetricDelta"] {{ color: #666 !important; }}

      .card {{
        background: #fff; border: 1px solid #ececec; border-radius: 12px;
        padding: 16px 18px; margin-bottom: 12px; color: #222;
      }}
      .card h4 {{ margin: 0 0 6px 0; font-size: 1rem; color: #15362b; }}
      .card p {{ color: #222; }}
      .card .muted {{ color: #777 !important; font-size: 0.85rem; margin: 0 0 8px 0; }}
      .pill {{
        display: inline-block; font-size: 0.72rem; font-weight: 600; border-radius: 999px;
        padding: 2px 10px; background: rgba(27,77,62,0.08); color: {GREEN}; margin-right: 6px;
      }}
      .pill-warn {{ background: rgba(192,57,43,0.1); color: {RED}; }}
      .priority-badge {{
        display: inline-block; font-size: 0.75rem; font-weight: 700; border-radius: 6px;
        padding: 3px 10px; color: white; margin-right: 8px;
      }}
      .priority-1 {{ background: {RED}; }}
      .priority-2 {{ background: #D68910; }}
      .priority-3 {{ background: #7F8C8D; }}

      /* Floating chat trigger + panel - keyed containers get a stable `.st-key-<key>` class */
      .st-key-chat_trigger {{
        position: fixed; bottom: 22px; right: 22px; z-index: 999; width: auto;
      }}
      .st-key-chat_trigger button {{
        background: {GREEN} !important; color: white !important; border: none !important;
        border-radius: 999px !important; padding: 10px 20px !important; font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
      }}
      .st-key-chat_panel {{
        position: fixed; bottom: 78px; right: 22px; z-index: 998;
        width: 360px; max-height: 480px; overflow-y: auto;
        background: white; border: 1px solid #e2e2e2; border-radius: 14px;
        padding: 14px; box-shadow: 0 8px 28px rgba(0,0,0,0.22); color: #222;
      }}
      .st-key-chat_panel p, .st-key-chat_panel span, .st-key-chat_panel div {{ color: #222; }}
      @media (max-width: 480px) {{
        .st-key-chat_panel {{ width: 88vw; right: 6vw; }}
      }}
    </style>
    """, unsafe_allow_html=True)


def hero(title: str, subtitle: str):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def finding_strip(html: str):
    st.markdown(f'<div class="finding-strip">{html}</div>', unsafe_allow_html=True)
