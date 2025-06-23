import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Agent Dashboard",
    page_icon="🤖",
)

st.write("# 🤖 Agent Dashboard")

st.sidebar.success("Select a page from the sidebar to manage specific aspects.")

st.markdown("Monitor your AI agent's memory and learning progress.")

# Helper function to read JSON files safely
def read_json_file(file_path):
    try:
        if Path(file_path).exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        st.error(f"Error reading {file_path}: {e}")
        return None

# Helper function to get agent memories
def get_agent_memories(limit=10):
    memory_locations = [
        Path('.cursor/memory-bank/context/agent_memory.json'),
        Path('.cursor/memory-bank/workflow/agent_memory.json'),
        Path('.cursor/memory-bank/agent_memory.json')
    ]
    
    for memory_file in memory_locations:
        if memory_file.exists():
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memories = json.load(f)
                    if isinstance(memories, list) and memories:
                        # Return the last 'limit' memories
                        return memories[-limit:] if len(memories) > limit else memories
            except Exception as e:
                st.error(f"Error reading memories from {memory_file}: {e}")
    
    return []

# Display Agent Memories
st.header("🧠 Agent Memory Timeline")
agent_memories = get_agent_memories(10)

if agent_memories:
    st.subheader("📖 Last 10 Agent Memories")
    st.write(f"Showing {len(agent_memories)} most recent memories (newest first)")
    
    # Use tabs for better organization (Present as default)
    tab1, tab2, tab3, tab4 = st.tabs(["🕐 Past", "⏰ Present", "🔮 Future", "🧠 Long Term"])
    
    with tab2:  # Present tab (default)
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
    
    with tab1:  # Past tab
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
    
    with tab3:  # Future tab
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
    
    with tab4:  # Long Term tab
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

else:
    st.info("No agent memories found. Memories will appear here as the agent works and learns.")

# Auto-refresh option
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 Auto-refresh")
auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)")
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()

# Quick actions
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Quick Actions")
if st.sidebar.button("🔄 Refresh Dashboard"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("💡 Use the pages in the sidebar to add requests, manage tasks, or edit memory.") 