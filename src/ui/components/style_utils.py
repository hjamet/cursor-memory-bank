import streamlit as st

def get_status_style(status):
    """Returns CSS style for a given task status."""
    if status == "BLOCKED":
        return "border: 2px solid red; border-radius: 5px; padding: 10px; margin-bottom: 10px;"
    # Default style for other statuses
    return "border: 1px solid #262730; border-radius: 5px; padding: 10px; margin-bottom: 10px;"

def apply_card_style(status):
    """Applies the CSS style for a task card."""
    style = get_status_style(status)
    st.markdown(f'<div style="{style}">', unsafe_allow_html=True)

def close_card_style():
    """Closes the styled div."""
    st.markdown('</div>', unsafe_allow_html=True) 