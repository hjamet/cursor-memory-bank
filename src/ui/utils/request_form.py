"""
Request form utilities for the Streamlit app.
Handles the UI for adding and editing user requests.
"""

import streamlit as st
import time
from streamlit_shortcuts import shortcut_button
from .request_manager import (
    get_next_request_id, save_uploaded_image, get_image_from_clipboard, 
    save_pasted_image, create_new_request, get_user_request, 
    delete_user_request, update_user_request
)


def render_add_request_tab():
    """Render the add request tab with form and submission logic"""
    # Use compact header with reduced spacing
    st.markdown("### Add New Request")
    st.caption("Submit a new request for the agent to process.")

    # Initialize session state
    if 'last_submitted_request_id' not in st.session_state:
        st.session_state.last_submitted_request_id = None
    if 'editing_request_id' not in st.session_state:
        st.session_state.editing_request_id = None
    if 'clear_request_form' not in st.session_state:
        st.session_state.clear_request_form = False
    if 'balloons_submitted_time' not in st.session_state:
        st.session_state.balloons_submitted_time = None
    if 'pasted_image_obj' not in st.session_state:
        st.session_state.pasted_image_obj = None

    # If a form was just submitted, clear the state before rendering widgets
    # Use a more elegant approach that allows balloons to play while clearing text
    if st.session_state.clear_request_form:
        current_time = time.time()
        # Check if enough time has passed since balloons animation (1.5 seconds - reduced delay)
        if (st.session_state.balloons_submitted_time is None or 
            current_time - st.session_state.balloons_submitted_time >= 1):
            # Clear the form silently after reduced delay
            st.session_state.request_content_area = ""
            st.session_state.pasted_image_obj = None
            st.session_state.clear_request_form = False
            st.session_state.balloons_submitted_time = None
        else:
            # Silent delay - no countdown message, just wait for balloons to finish
            # The balloons animation plays while we silently wait for the optimal moment to clear
            # This provides the best user experience: balloons visible + clean form clearing
            st.rerun()

    # If editing, load the content
    request_content_default = ""
    if st.session_state.editing_request_id:
        request_to_edit = get_user_request(st.session_state.editing_request_id)
        if request_to_edit:
            request_content_default = request_to_edit.get("content", "")
    
    # Use session state value if available, otherwise use default
    if 'request_content_area' in st.session_state and not st.session_state.editing_request_id:
        # When not editing, use session state value (which may be empty after clearing)
        text_area_value = st.session_state.request_content_area
    else:
        # When editing or first load, use default value
        text_area_value = request_content_default

    request_content = st.text_area(
        "Request Description", 
        value=text_area_value, 
        height=250, 
        placeholder="Please provide a detailed description of your request...", 
        label_visibility="collapsed", 
        key="request_content_area"
    )
    
    with st.expander("📎 Attach an Image (Optional)"):
        col1, col2 = st.columns(2)
        with col1:
            uploaded_image = st.file_uploader(
                "Upload an image",
                type=['png', 'jpg', 'jpeg', 'gif'],
                label_visibility="collapsed"
            )

        with col2:
            if shortcut_button("📋 Paste from clipboard", "ctrl+v", help="Press Ctrl+V to paste an image from your clipboard."):
                pasted_image = get_image_from_clipboard()
                if pasted_image:
                    st.session_state.pasted_image_obj = pasted_image
                    st.toast("Image captured from clipboard! Preview below.")
                    uploaded_image = None # Clear file uploader
                else:
                    st.warning("No image found on clipboard.")
    
        # Display preview for uploaded or pasted image
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded image preview", width=300)
            st.session_state.pasted_image_obj = None  # Clear pasted image if user uploads
        elif st.session_state.pasted_image_obj:
            st.image(st.session_state.pasted_image_obj, caption="Pasted image preview", width=300)

    # Determine button label and action
    is_editing = st.session_state.editing_request_id is not None
    submit_label = "Update Request" if is_editing else "Submit New Request"
    
    # Use shortcut_button with Ctrl+Enter shortcut
    if shortcut_button(submit_label, "ctrl+enter", type="primary", use_container_width=True):
        if request_content:
            if is_editing:
                # Update existing request
                if update_user_request(st.session_state.editing_request_id, request_content):
                    st.success(f"Request #{st.session_state.editing_request_id} updated successfully!")
                    st.session_state.last_submitted_request_id = st.session_state.editing_request_id
                    st.session_state.editing_request_id = None
                    st.session_state.clear_request_form = True # Clear form on next run
                    # Force a rerun to clear the form immediately after successful update
                    st.rerun()
                else:
                    st.error("Failed to update the request.")
            else:
                # Create new request
                next_id = get_next_request_id()
                image_meta = None
                if uploaded_image:
                    image_meta = save_uploaded_image(uploaded_image, next_id)
                elif st.session_state.pasted_image_obj:
                    image_meta = save_pasted_image(st.session_state.pasted_image_obj, next_id)

                if create_new_request(request_content, image_meta):
                    st.success(f"Request #{next_id} submitted successfully!")
                    st.balloons()  # Celebration animation for successful submission
                    st.session_state.balloons_submitted_time = time.time()  # Record animation start time
                    st.session_state.pasted_image_obj = None
                    st.session_state.last_submitted_request_id = next_id
                    st.session_state.clear_request_form = True # Clear form after animation delay
                    # Note: Form will be cleared after 1.5 seconds to allow balloons animation
                else:
                    st.error("Failed to submit the request. Please check the logs.")
        else:
            st.warning("Please enter a description for your request.")

    # Display the last submitted request for editing/deleting
    if st.session_state.last_submitted_request_id and st.session_state.editing_request_id is None:
        st.markdown("---")
        st.subheader("Last Submitted Request")
        last_request = get_user_request(st.session_state.last_submitted_request_id)

        if last_request:
            if last_request.get("status") == "new":
                with st.container(border=True):
                    st.markdown(f"**Request #{last_request['id']}** (Status: {last_request['status']})")
                    st.info(last_request['content'])

                    col1, col2, col3 = st.columns([1, 1, 4])
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_{last_request['id']}"):
                            st.session_state.editing_request_id = last_request['id']
                            st.rerun()
                    with col2:
                        if st.button("❌ Delete", key=f"delete_{last_request['id']}"):
                            if delete_user_request(last_request['id']):
                                st.toast(f"Request #{last_request['id']} deleted.")
                                st.session_state.last_submitted_request_id = None
                                st.rerun()
                            else:
                                st.error("Failed to delete the request.")
            else:
                 st.info(f"Request #{last_request['id']} has already been processed by the agent and cannot be modified here.")

    # This block was causing state modification errors and is no longer needed.
    # The new 'clear_request_form' flag handles state reset safely.
    if st.session_state.get('form_submitted'):
        st.session_state.form_submitted = False
        st.rerun() 