"""Floating chat widget - "Ask about this data."

Answers are grounded in `build_context()` below (national figures, archetypes, lookalike
counts, insights) so a connected LLM answers from this dashboard's own numbers, not generic
knowledge. No API is wired in yet - see `get_ai_response()`.
"""
import streamlit as st


def build_context(facts, archetypes, insights) -> str:
    """Flattens the dashboard's grounded numbers into text for an LLM's system/context prompt."""
    lines = [
        "You are the assistant for the Rwanda Insurance Gap Radar dashboard (FinScope 2024, "
        f"{facts['n_respondents']:,} adults). Answer only from the figures below - if something "
        "isn't covered here, say so rather than guessing. However, if there's something outside of this data that you can infer from the dashboard's numbers, you may do so. You can also refer to the trusted sources for some figures like total population in rwanda. Additionally, when stating numbers, don't say 0.59 million (or any decimal million) as written in the dashboard, instead say 590,000 or 590K. If you need to refer to a percentage, round it to the nearest whole number.",
        "",
        f"National: {facts['financial_inclusion']:.0%} financially included, "
        f"{facts['health_cover']:.1%} hold health cover, {facts['any_uptake']:.1%} hold any "
        f"non-health insurance or pension. Insurance gap {facts['insurance_uptake']:.1%}, "
        f"pension gap {facts['pension_uptake']:.1%}.",
        "",
        "Archetypes (who already holds each product):",
    ]
    for gap, label in [("insurance_uptake", "Insurance"), ("pension_uptake", "Pension")]:
        for a in archetypes.get(gap, []):
            lines.append(f"  [{label}] {a['name']}: {a['adults_k']/1000:.2f}M adults, "
                          f"avg age {a['mean_age']:.0f}, vehicle {a['pct_owns_vehicle']:.0%}, "
                          f"mobile money {a['pct_mobile_money']:.0%}")
    lines.append("")
    lines.append("Key insights:")
    for i in insights:
        lines.append(f"  - {i}")
    return "\n".join(lines)


def get_ai_response(question: str, context: str) -> str:
    """Calls Gemini via LangChain (`langchain-google-genai`) if a key is configured;
    otherwise returns a clear "not connected" message instead of crashing.

    Setup: put your key in `.streamlit/secrets.toml` (git-ignored) as:
        GEMINI_API_KEY = "..."
    or add it in the Streamlit Community Cloud app's Settings -> Secrets panel. Never put a
    literal key in this file - it goes on GitHub.

    Direct google-genai SDK alternative, if you'd rather skip LangChain:
        from google import genai
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        reply = client.models.generate_content(model="gemini-3.8-flash", contents=f"{context}\\n\\nQuestion: {question}")
        return reply.text
    """
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None  # no secrets.toml at all yet - st.secrets.get() still raises in that case
    if not api_key:
        return (
            "AI answers aren't connected yet - add GEMINI_API_KEY in `.streamlit/secrets.toml` "
            "(see the docstring in `ai_chat.get_ai_response()`). "
            "Meanwhile, the Insights tab and the tables in this dashboard are grounded in the "
            "exact same data this question would be answered from."
        )

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        # max_retries=1, timeout=20s: the default max_retries=6 can quietly compound into a
        # multi-minute hang when the model is under heavy load (seen during testing) - fail
        # fast instead of freezing the chat UI.
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash", google_api_key=api_key, timeout=20, max_retries=1,
        )
        reply = llm.invoke(f"{context}\n\nQuestion: {question}")
        content = reply.content
        if isinstance(content, str):
            return content
        # Newer Gemini models (3.x) return a list of content blocks (text + an internal
        # "thinking signature" block) instead of a plain string - keep only the text parts.
        return "".join(
            block.get("text", "") for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip() or "(empty response)"
    except Exception as e:
        return f"AI request failed ({e.__class__.__name__}): {e}"


def render_floating_chat(context: str):
    st.session_state.setdefault("chat_open", False)
    st.session_state.setdefault("chat_messages", [])

    with st.container(key="chat_trigger"):
        label = "Close" if st.session_state.chat_open else "Ask about this data"
        if st.button(label, key="chat_toggle_btn"):
            st.session_state.chat_open = not st.session_state.chat_open
            st.rerun()

    if not st.session_state.chat_open:
        return

    with st.container(key="chat_panel"):
        st.markdown("**Ask about this data**")
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        question = st.chat_input("Ask about an archetype, a segment, a brief...")
        if question:
            st.session_state.chat_messages.append({"role": "user", "content": question})
            answer = get_ai_response(question, context)
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            st.rerun()
