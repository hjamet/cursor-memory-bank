"""
Memory UI components for displaying agent memories and long-term memories.
Handles the rendering of memory timelines and memory management interfaces.
"""

import streamlit as st
from datetime import datetime
import memory_data_manager
import file_operations
save_long_term_memories = memory_data_manager.save_long_term_memories
fuzzy_search_memories = memory_data_manager.fuzzy_search_memories


def _check_and_notify_new_present_memories(agent_memories):
    """
    Checks for new present memories and shows a toast notification if they are new.
    Updates the session state to mark them as seen.
    """
    if not agent_memories:
        return
    
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
    
    # Show toast notifications for new memories
    for memory in new_present_memories:
        present_content = memory.get('present', '').strip()
        timestamp = memory.get('timestamp', '')
        
        # Create a more informative notification message
        if len(present_content) > 60:
            preview = present_content[:60] + "..."
        else:
            preview = present_content
        
        # Format timestamp for display
        try:
            formatted_time = timestamp[:19].replace('T', ' ') if timestamp else 'Unknown'
        except:
            formatted_time = 'Unknown'
        
        # Show toast notification
        st.toast(
            f"🧠 New agent memory recorded at {formatted_time}: {preview}", 
            icon="✨"
        )
        
        # Mark as seen
        st.session_state.seen_present_memories.add(timestamp)


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