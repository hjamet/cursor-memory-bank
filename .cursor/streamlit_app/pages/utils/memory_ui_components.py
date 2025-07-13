"""
Memory UI components for displaying agent memories and long-term memories.
Handles the rendering of memory timelines and memory management interfaces.
"""

import streamlit as st
from datetime import datetime
import memory_data_manager
import file_operations
import time
import uuid
import markdown
import html
import re
save_long_term_memories = memory_data_manager.save_long_term_memories
fuzzy_search_memories = memory_data_manager.fuzzy_search_memories


def _apply_enhanced_toast_styles():
    """
    Apply enhanced CSS styles for toast notifications to make them more visible,
    larger, and with better appearance.
    """
    enhanced_toast_css = """
    <style>
    /* Enhanced Toast Notification Styles */
    .stToast {
        background-color: #1f2937 !important;
        border: 2px solid #3b82f6 !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
        min-width: 350px !important;
        max-width: 500px !important;
        padding: 16px 20px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #f9fafb !important;
        backdrop-filter: blur(10px) !important;
        z-index: 9999 !important;
    }
    
    .stToast > div {
        background: transparent !important;
        color: #f9fafb !important;
        line-height: 1.5 !important;
        word-wrap: break-word !important;
        white-space: pre-wrap !important;
    }
    
    .stToast .stToast-content {
        display: flex !important;
        align-items: flex-start !important;
        gap: 12px !important;
        width: 100% !important;
    }
    
    .stToast .stToast-icon {
        font-size: 20px !important;
        flex-shrink: 0 !important;
        margin-top: 2px !important;
    }
    
    .stToast .stToast-message {
        flex: 1 !important;
        font-size: 14px !important;
        line-height: 1.4 !important;
        color: #f9fafb !important;
    }
    
    /* Animation enhancements */
    .stToast {
        animation: enhanced-slide-in 0.3s ease-out !important;
    }
    
    @keyframes enhanced-slide-in {
        from {
            transform: translateX(100%) scale(0.9);
            opacity: 0;
        }
        to {
            transform: translateX(0) scale(1);
            opacity: 1;
        }
    }
    
    /* Hover effects for better interaction */
    .stToast:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4) !important;
        border-color: #60a5fa !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    /* Memory-specific toast styling */
    .stToast.memory-toast {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%) !important;
        border-color: #60a5fa !important;
    }
    
    .stToast.memory-toast:hover {
        border-color: #93c5fd !important;
    }
    </style>
    """
    st.markdown(enhanced_toast_css, unsafe_allow_html=True)


def _show_enhanced_toast(message, icon="✨", toast_type="memory"):
    """
    Display an enhanced toast notification with improved styling and longer visibility.
    
    Args:
        message (str): The message to display
        icon (str): The icon to show with the message
        toast_type (str): Type of toast for styling ('memory', 'success', 'info')
    """
    # Apply enhanced styles first
    _apply_enhanced_toast_styles()
    
    # Create the toast with improved message formatting
    formatted_message = f"{message}"
    
    # Show the toast notification
    toast_obj = st.toast(formatted_message, icon=icon)
    
    return toast_obj


def create_enhanced_notification(message, icon="ℹ️", notification_type="info", duration_hint="extended"):
    """
    Create an enhanced notification toast with improved styling and appearance.
    
    Args:
        message (str): The notification message to display
        icon (str): The icon to show (default: "ℹ️")
        notification_type (str): Type of notification ('info', 'success', 'warning', 'error', 'memory')
        duration_hint (str): Hint for duration ('standard', 'extended') - note: actual duration is still 4s
    
    Returns:
        toast object: The Streamlit toast object for potential updates
    """
    # Apply enhanced styles
    _apply_enhanced_toast_styles()
    
    # Format message based on type
    if notification_type == "memory":
        formatted_message = f"🧠 {message}"
        icon = "🧠" if icon == "ℹ️" else icon
    elif notification_type == "success":
        formatted_message = f"✅ {message}"
        icon = "✅" if icon == "ℹ️" else icon
    elif notification_type == "warning":
        formatted_message = f"⚠️ {message}"
        icon = "⚠️" if icon == "ℹ️" else icon
    elif notification_type == "error":
        formatted_message = f"❌ {message}"
        icon = "❌" if icon == "ℹ️" else icon
    else:  # info
        formatted_message = message
    
    # Add duration hint to message (visual cue since we can't change actual duration)
    if duration_hint == "extended":
        formatted_message += "\n\n💡 Notification importante - prenez le temps de la lire"
    
    # Create and return the toast
    return st.toast(formatted_message, icon=icon)


def _apply_custom_notification_styles():
    """
    Apply CSS styles for custom notification system that bypasses st.toast() limitations.
    """
    custom_notification_css = """
    <style>
    /* Custom Notification System - Alternative to st.toast() */
    .custom-notification-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        pointer-events: none;
        width: 400px;
        max-width: 90vw;
    }
    
    .custom-notification {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
        border: 2px solid #60a5fa;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        padding: 16px 20px;
        margin-bottom: 10px;
        color: #f9fafb;
        font-size: 14px;
        font-weight: 500;
        backdrop-filter: blur(10px);
        animation: slideInRight 0.3s ease-out;
        pointer-events: auto;
        position: relative;
        word-wrap: break-word;
        line-height: 1.5;
    }
    
    .custom-notification.success {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        border-color: #10b981;
    }
    
    .custom-notification.warning {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        border-color: #f59e0b;
    }
    
    .custom-notification.error {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        border-color: #ef4444;
    }
    
    .custom-notification.info {
        background: linear-gradient(135deg, #0369a1 0%, #0284c7 100%);
        border-color: #0ea5e9;
    }
    
    .custom-notification-content {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        width: 100%;
    }
    
    .custom-notification-icon {
        font-size: 20px;
        flex-shrink: 0;
        margin-top: 2px;
    }
    
    .custom-notification-message {
        flex: 1;
        font-size: 14px;
        line-height: 1.4;
        color: #f9fafb;
    }
    
    .custom-notification-message p {
        margin: 0 0 8px 0;
    }
    
    .custom-notification-message p:last-child {
        margin-bottom: 0;
    }
    
    .custom-notification-message strong {
        font-weight: 600;
    }
    
    .custom-notification-message em {
        font-style: italic;
    }
    
    .custom-notification-message code {
        background: rgba(255, 255, 255, 0.1);
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
    }
    
    .custom-notification-close {
        position: absolute;
        top: 8px;
        right: 10px;
        background: none;
        border: none;
        color: #f9fafb;
        cursor: pointer;
        font-size: 18px;
        font-weight: bold;
        opacity: 0.7;
        transition: opacity 0.2s;
    }
    
    .custom-notification-close:hover {
        opacity: 1;
    }
    
    .custom-notification-progress {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 3px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 0 0 10px 10px;
        transition: width linear;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%) scale(0.9);
            opacity: 0;
        }
        to {
            transform: translateX(0) scale(1);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0) scale(1);
            opacity: 1;
        }
        to {
            transform: translateX(100%) scale(0.9);
            opacity: 0;
        }
    }
    
    .custom-notification.fade-out {
        animation: slideOutRight 0.3s ease-in forwards;
    }
    
    .custom-notification:hover {
        transform: scale(1.02);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
        transition: all 0.2s ease-in-out;
    }
    
    .custom-notification:hover .custom-notification-progress {
        animation-play-state: paused;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .custom-notification-container {
            width: 350px;
            right: 10px;
            top: 10px;
        }
        
        .custom-notification {
            padding: 12px 16px;
            font-size: 13px;
        }
        
        .custom-notification-icon {
            font-size: 18px;
        }
    }
    </style>
    """
    st.markdown(custom_notification_css, unsafe_allow_html=True)


def _create_notification_container():
    """
    Create the notification container element for custom notifications.
    """
    if 'notification_container_created' not in st.session_state:
        st.session_state.notification_container_created = True
        container_html = '<div id="custom-notification-container" class="custom-notification-container"></div>'
        st.markdown(container_html, unsafe_allow_html=True)


def _render_markdown_content(content):
    """
    Safely render markdown content to HTML with proper escaping.
    
    Args:
        content (str): The markdown content to render
        
    Returns:
        str: Safe HTML content
    """
    # First, escape any existing HTML tags in the content before markdown processing
    
    # Escape dangerous tags before markdown processing
    dangerous_tags = ['script', 'iframe', 'object', 'embed', 'link', 'style', 'form', 'input']
    
    for tag in dangerous_tags:
        # Use regex to match tags with any attributes
        pattern = f'<{tag}\\b[^>]*>'
        content = re.sub(pattern, lambda m: html.escape(m.group(0)), content, flags=re.IGNORECASE)
        
        # Also handle closing tags
        pattern = f'</{tag}>'
        content = re.sub(pattern, lambda m: html.escape(m.group(0)), content, flags=re.IGNORECASE)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(content, extensions=['nl2br'])
    
    return html_content


def show_custom_notification(message, icon="🔔", notification_type="info", duration=10, enable_markdown=True):
    """
    Display a custom notification with configurable duration and markdown support.
    This bypasses st.toast() limitations.
    
    Args:
        message (str): The notification message (supports markdown if enabled)
        icon (str): The icon to display (default: "🔔")
        notification_type (str): Type of notification ('info', 'success', 'warning', 'error', 'memory')
        duration (int): Duration in seconds (5-15 seconds, default: 10)
        enable_markdown (bool): Whether to process markdown formatting (default: True)
    
    Returns:
        str: Notification ID for potential removal
    """
    # Apply custom styles
    _apply_custom_notification_styles()
    _create_notification_container()
    
    # Initialize notifications in session state
    if 'custom_notifications' not in st.session_state:
        st.session_state.custom_notifications = []
    
    # Validate duration
    duration = max(5, min(15, duration))
    
    # Generate unique notification ID
    notification_id = str(uuid.uuid4())
    
    # Process message content
    if enable_markdown:
        processed_message = _render_markdown_content(message)
    else:
        processed_message = html.escape(message).replace('\n', '<br>')
    
    # Set notification type class
    type_class = notification_type if notification_type in ['info', 'success', 'warning', 'error'] else 'info'
    if notification_type == "memory":
        type_class = "info"  # Use info styling for memory notifications
    
    # Create notification HTML
    notification_html = f"""
    <script>
    (function() {{
        const container = document.getElementById('custom-notification-container');
        if (!container) {{
            console.warn('Custom notification container not found');
            return;
        }}
        
        const notification = document.createElement('div');
        notification.id = 'notification-{notification_id}';
        notification.className = 'custom-notification {type_class}';
        notification.innerHTML = `
            <div class="custom-notification-content">
                <div class="custom-notification-icon">{icon}</div>
                <div class="custom-notification-message">{processed_message}</div>
            </div>
            <button class="custom-notification-close" onclick="removeNotification('{notification_id}')">&times;</button>
            <div class="custom-notification-progress" id="progress-{notification_id}"></div>
        `;
        
        container.appendChild(notification);
        
        // Progress bar animation
        const progressBar = document.getElementById('progress-{notification_id}');
        if (progressBar) {{
            progressBar.style.width = '100%';
            progressBar.style.transition = 'width {duration}s linear';
            setTimeout(() => {{
                progressBar.style.width = '0%';
            }}, 100);
        }}
        
        // Auto-remove after duration
        setTimeout(() => {{
            removeNotification('{notification_id}');
        }}, {duration * 1000});
        
        // Global remove function
        window.removeNotification = function(notificationId) {{
            const notif = document.getElementById('notification-' + notificationId);
            if (notif) {{
                notif.classList.add('fade-out');
                setTimeout(() => {{
                    if (notif.parentNode) {{
                        notif.parentNode.removeChild(notif);
                    }}
                }}, 300);
            }}
        }};
    }})();
    </script>
    """
    
    # Display the notification
    st.markdown(notification_html, unsafe_allow_html=True)
    
    # Store notification info in session state
    st.session_state.custom_notifications.append({
        'id': notification_id,
        'message': message,
        'type': notification_type,
        'timestamp': time.time(),
        'duration': duration
    })
    
    # Clean up old notifications from session state
    current_time = time.time()
    st.session_state.custom_notifications = [
        notif for notif in st.session_state.custom_notifications 
        if current_time - notif['timestamp'] < notif['duration'] + 5
    ]
    
    return notification_id


def create_enhanced_notification_v2(message, icon="ℹ️", notification_type="info", duration=10, enable_markdown=True):
    """
    Enhanced notification system v2 with full markdown support and configurable duration.
    This is the new alternative to st.toast() with better features.
    
    Args:
        message (str): The notification message (supports markdown)
        icon (str): The icon to show (default: "ℹ️")
        notification_type (str): Type of notification ('info', 'success', 'warning', 'error', 'memory')
        duration (int): Duration in seconds (5-15 seconds, default: 10)
        enable_markdown (bool): Whether to process markdown formatting (default: True)
    
    Returns:
        str: Notification ID for potential removal
    """
    # Set appropriate icons based on type
    if notification_type == "memory" and icon == "ℹ️":
        icon = "🧠"
    elif notification_type == "success" and icon == "ℹ️":
        icon = "✅"
    elif notification_type == "warning" and icon == "ℹ️":
        icon = "⚠️"
    elif notification_type == "error" and icon == "ℹ️":
        icon = "❌"
    
    # Add type prefix to message for better context
    if notification_type == "memory":
        formatted_message = f"**Nouveau souvenir:**\n\n{message}"
    elif notification_type == "success":
        formatted_message = f"**Succès:**\n\n{message}"
    elif notification_type == "warning":
        formatted_message = f"**Attention:**\n\n{message}"
    elif notification_type == "error":
        formatted_message = f"**Erreur:**\n\n{message}"
    else:
        formatted_message = message
    
    return show_custom_notification(
        message=formatted_message,
        icon=icon,
        notification_type=notification_type,
        duration=duration,
        enable_markdown=enable_markdown
    )


def _check_and_notify_new_present_memories_v2(agent_memories):
    """
    Enhanced version of memory notification checker using the new custom notification system.
    """
    if not agent_memories:
        return
    
    # Initialize session state for tracking seen memories
    if 'seen_present_memories' not in st.session_state:
        st.session_state.seen_present_memories = set()
    
    # Filter memories with valid present content and timestamps
    valid_present_memories = [
        m for m in agent_memories 
        if m.get('present') and m.get('present').strip() 
        and m.get('present') != 'N/A' 
        and m.get('timestamp')
    ]
    
    # Check for new memories not yet seen
    new_present_memories = [
        m for m in valid_present_memories
        if m['timestamp'] not in st.session_state.seen_present_memories
    ]
    
    # Show custom notifications for new memories
    for memory in new_present_memories:
        present_content = memory.get('present', '').strip()
        timestamp = memory.get('timestamp', '')
        
        # Create a more informative notification message with markdown formatting
        if len(present_content) > 200:
            preview = present_content[:200] + "..."
        else:
            preview = present_content
        
        # Format the message with timestamp and markdown
        formatted_timestamp = timestamp[:19].replace('T', ' ') if timestamp else 'Unknown time'
        notification_message = f"**Timestamp:** {formatted_timestamp}\n\n{preview}"
        
        # Show custom notification with longer duration and markdown support
        create_enhanced_notification_v2(
            message=notification_message,
            icon="🧠",
            notification_type="memory",
            duration=12,  # 12 seconds duration
            enable_markdown=True
        )
        
        # Mark as seen
        st.session_state.seen_present_memories.add(timestamp)


def _check_and_notify_new_present_memories(agent_memories):
    """
    Original function for backward compatibility - now uses the new custom notification system.
    Checks for new present memories and shows enhanced notifications if they are new.
    Updates the session state to mark them as seen.
    """
    # Use the new enhanced version
    _check_and_notify_new_present_memories_v2(agent_memories)


def display_agent_memory_timeline(agent_memories):
    """Display agent memory timeline with tabs for different time perspectives and toast notifications for new present memories"""
    if not agent_memories:
        st.info("No agent memories found. Memories will appear here as the agent works and learns.")
        return
    
    # Initialize session state for tracking seen memories
    if 'seen_present_memories' not in st.session_state:
        st.session_state.seen_present_memories = set()
    
    # Check for new present memories and show toast notifications
    _check_and_notify_new_present_memories(agent_memories)
    
    st.subheader("📖 Last 10 Agent Memories")
    st.write(f"Showing {len(agent_memories)} most recent memories (newest first)")
    
    # Use tabs for better organization (Present as default)
    mem_tab1, mem_tab2, mem_tab3, mem_tab4 = st.tabs(["⏰ Present", "🕐 Past", "🔮 Future", "🧠 Long Term"])
    
    with mem_tab1:  # Present tab (default)
        st.write("**Present Reality - Most Recent Memories**")
        for i, memory in enumerate(reversed(agent_memories)):  # Most recent first
            memory_id = len(agent_memories) - i
            timestamp = memory.get('timestamp', 'Unknown')[:19].replace('T', ' ') if memory.get('timestamp') else 'Unknown'
            
            st.markdown(f"### 💭 Memory #{memory_id} - {timestamp}")
            present_content = memory.get('present', 'N/A')
            if present_content and present_content != 'N/A':
                st.write(present_content)
            else:
                st.info("No present reality recorded")
            
            st.caption(f"📅 Recorded: {timestamp}")
            st.markdown("---")
    
    with mem_tab2:  # Past tab
        st.write("**Past Context - Historical Memories**")
        for i, memory in enumerate(reversed(agent_memories)):  # Most recent first
            memory_id = len(agent_memories) - i
            timestamp = memory.get('timestamp', 'Unknown')[:19].replace('T', ' ') if memory.get('timestamp') else 'Unknown'
            
            st.markdown(f"### 💭 Memory #{memory_id} - {timestamp}")
            past_content = memory.get('past', 'N/A')
            if past_content and past_content != 'N/A':
                st.write(past_content)
            else:
                st.info("No past context recorded")
            
            st.caption(f"📅 Recorded: {timestamp}")
            st.markdown("---")
    
    with mem_tab3:  # Future tab
        st.write("**Future Plans - Upcoming Actions**")
        for i, memory in enumerate(reversed(agent_memories)):  # Most recent first
            memory_id = len(agent_memories) - i
            timestamp = memory.get('timestamp', 'Unknown')[:19].replace('T', ' ') if memory.get('timestamp') else 'Unknown'
            
            st.markdown(f"### 💭 Memory #{memory_id} - {timestamp}")
            future_content = memory.get('future', 'N/A')
            if future_content and future_content != 'N/A':
                st.write(future_content)
            else:
                st.info("No future plans recorded")
            
            st.caption(f"📅 Recorded: {timestamp}")
            st.markdown("---")
    
    with mem_tab4:  # Long Term tab
        st.write("**Long Term Memory - Persistent Knowledge**")
        for i, memory in enumerate(reversed(agent_memories)):  # Most recent first
            memory_id = len(agent_memories) - i
            timestamp = memory.get('timestamp', 'Unknown')[:19].replace('T', ' ') if memory.get('timestamp') else 'Unknown'
            
            long_term_content = memory.get('long_term_memory', '')
            if long_term_content and long_term_content.strip():
                st.markdown(f"### 💭 Memory #{memory_id} - {timestamp}")
                st.write(long_term_content)
                st.caption(f"📅 Recorded: {timestamp}")
                st.markdown("---")
        
        # Show message if no long-term memories found
        long_term_count = sum(1 for m in agent_memories if m.get('long_term_memory', '').strip())
        if long_term_count == 0:
            st.info("No long term memories recorded yet")
    
    # Summary section
    st.markdown("---")
    with st.expander("📊 Memory Summary", expanded=False):
        st.write(f"**Total memories displayed:** {len(agent_memories)}")
        
        # Count memories with long-term content
        long_term_count = sum(1 for m in agent_memories if m.get('long_term_memory', '').strip())
        st.write(f"**Memories with long-term insights:** {long_term_count}")
        
        # Show date range
        if len(agent_memories) > 1:
            oldest = agent_memories[0].get('timestamp', '')[:19].replace('T', ' ')
            newest = agent_memories[-1].get('timestamp', '')[:19].replace('T', ' ')
            st.write(f"**Time range:** {oldest} to {newest}")


def display_long_term_memories(memories, search_query=""):
    """Display and manage long-term memories with search and edit capabilities"""
    # Filter memories based on search query
    filtered_memories = fuzzy_search_memories(memories, search_query)
    
    if search_query:
        st.info(f"Found {len(filtered_memories)} matching memories for query: \"{search_query}\"")

    if filtered_memories:
        st.subheader(f"Stored Memories ({len(filtered_memories)} / {len(memories)})")
        
        # Display memories directly without accordions
        for i, memory in enumerate(filtered_memories):
            # Skip non-dictionary memory objects to prevent AttributeError
            if not isinstance(memory, dict):
                st.warning(f"⚠️ Memory #{i+1} has invalid format (expected dictionary, got {type(memory).__name__}). Skipping.")
                continue
                
            # Create a container for each memory with visual separation
            memory_container = st.container()
            with memory_container:
                # Header with memory number and timestamp
                st.markdown(f"### 🧠 Memory #{i+1}")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown("**Content:**")
                    
                    # Check if this memory is being edited
                    edit_key = f"edit_memory_{i}"
                    if edit_key not in st.session_state:
                        st.session_state[edit_key] = False
                    
                    if st.session_state[edit_key]:
                        # Edit mode: show text area
                        new_content = st.text_area(
                            "Edit memory content:",
                            value=memory.get('content', ''),
                            height=100,
                            key=f"edit_content_{i}"
                        )
                        
                        # Save/Cancel buttons
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 Save", key=f"save_{i}"):
                                # Find the actual index in the original memories list
                                original_index = memories.index(memory)
                                memories[original_index]['content'] = new_content
                                memories[original_index]['timestamp'] = datetime.now().isoformat()  # Update timestamp
                                
                                if save_long_term_memories(memories):
                                    st.success("Memory updated!")
                                    st.session_state[edit_key] = False
                                    st.rerun()
                        
                        with col_cancel:
                            if st.button("❌ Cancel", key=f"cancel_{i}"):
                                st.session_state[edit_key] = False
                                st.rerun()
                    else:
                        # Display mode: show content directly
                        st.markdown(f"*{memory.get('content', 'No content')}*")
                    
                    # Show embedding info if available
                    if memory.get('embedding'):
                        st.caption(f"📊 Embedding: {len(memory['embedding'])} dimensions")
                
                with col2:
                    st.markdown("**Info:**")
                    timestamp = memory.get('timestamp', 'Unknown')
                    if timestamp != 'Unknown':
                        # Format timestamp nicely
                        try:
                            formatted_date = timestamp[:19].replace('T', ' ')
                            st.write(f"**Date:** {formatted_date}")
                        except:
                            st.write(f"**Date:** {timestamp}")
                    else:
                        st.write(f"**Date:** {timestamp}")
                    
                    st.markdown("**Actions:**")
                    
                    # Edit button
                    if not st.session_state[edit_key]:
                        if st.button(f"✏️ Edit", key=f"edit_btn_{i}", help="Edit memory content"):
                            st.session_state[edit_key] = True
                            st.rerun()
                    
                    # Delete button (direct deletion without confirmation)
                    if st.button(f"🗑️ Delete", key=f"delete_btn_{i}", help="Delete this memory"):
                        # Find the actual index in the original memories list and delete
                        try:
                            original_index = memories.index(memory)
                            memories.pop(original_index)
                            if save_long_term_memories(memories):
                                st.success("Memory deleted!")
                                st.rerun()
                        except ValueError:
                            st.error("Error: Memory not found for deletion.")
                
                # Add visual separator between memories
                st.markdown("---")
    elif search_query:
        st.warning(f"No memories found matching your search for \"{search_query}\".")
    else:
        st.info("No long-term memories found.")


def display_memory_search_bar():
    """Display search bar for memories with clear functionality"""
    st.subheader("🔍 Search Memories")
    search_col1, search_col2 = st.columns([4, 1])
    with search_col1:
        search_query = st.text_input(
            "Search by keyword in memory content:",
            key="memory_search_query",
            placeholder="e.g., 'database schema', 'API key'"
        )
    with search_col2:
        if st.button("❌ Clear Search", key="clear_memory_search"):
            st.session_state.memory_search_query = ""
            st.rerun()
    
    return search_query


def display_add_memory_form(memories):
    """Display form for adding new memories"""
    st.subheader("➕ Add New Memory")
    with st.form("add_memory_form", clear_on_submit=True):
        new_memory_content = st.text_area(
            "Memory Content:",
            height=150,
            placeholder="Describe something important you learned or want to remember...",
            help="This will be stored as a long-term memory with semantic search capabilities."
        )
        
        if st.form_submit_button("➕ Add Memory"):
            if new_memory_content.strip():
                new_memory = {
                    'content': new_memory_content.strip(),
                    'timestamp': datetime.now().isoformat(),
                    'embedding': None  # Will be generated by the semantic search system
                }
                
                memories.append(new_memory)
                
                if save_long_term_memories(memories):
                    st.success("✅ New memory added!")
                    st.rerun()
            else:
                st.error("Please enter memory content.")


def display_text_editor_tab(tab_name, content, file_path, save_function, key_prefix):
    """Display a text editor tab with auto-save functionality"""
    st.header(f"{tab_name}")
    
    if tab_name == "📋 Project Brief":
        st.markdown("Edit the main project description and objectives.")
        help_text = "Describe your project's goals, scope, and key requirements."
    else:  # Tech Context
        st.markdown("Manage technical specifications, architecture, and constraints.")
        help_text = "Describe technical architecture, frameworks, constraints, and requirements."
    
    # Edit content with auto-save
    updated_content = st.text_area(
        f"{tab_name.split()[-1]} Content:",
        value=content,
        height=300,
        help=help_text,
        key=f"{key_prefix}_editor"
    )
    
    # Auto-save on change
    if updated_content != content:
        if save_function(file_path, updated_content):
            st.success(f"✅ {tab_name.split()[-1]} updated automatically!")
            st.rerun()
    
    # Clear button
    if st.button(f"🗑️ Clear {tab_name.split()[-1]}", key=f"clear_{key_prefix}"):
        if save_function(file_path, ""):
            st.success(f"{tab_name.split()[-1]} cleared!")
            st.rerun()
    
    # Show current stats
    if content:
        st.subheader(f"📊 {tab_name.split()[-1]} Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Characters", len(content))
        
        with col2:
            word_count = len(content.split())
            st.metric("Words", word_count)
        
        with col3:
            line_count = len(content.split('\n'))
            st.metric("Lines", line_count) 