from textwrap import dedent

import streamlit as st


def normalize_html(markup: str) -> str:
    """Prevent indented multiline HTML from becoming Markdown code blocks."""
    return "\n".join(line.strip() for line in dedent(markup).splitlines() if line.strip())


def render_html(markup: str) -> None:
    st.markdown(normalize_html(markup), unsafe_allow_html=True)
