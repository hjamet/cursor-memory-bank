import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Memory Bank UI! 👋")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    This is a user interface to interact with the Memory Bank of the AI agent.
    **👈 Select a page from the sidebar** to see what the agent is up to.
    """
) 