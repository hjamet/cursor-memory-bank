import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Memory Management", page_icon="🧠")

st.markdown("# 🧠 Memory Management")
st.sidebar.header("Memory Management")

st.markdown("Manage your project's memory: preferences, long-term memories, project brief, and technical context.")

# Helper functions
def load_json_file(file_path):
    """Load a JSON file and return its content"""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
    return None

def save_json_file(file_path, data):
    """Save data to a JSON file"""
    try:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving {file_path}: {e}")
        return False

def load_text_file(file_path):
    """Load a text file and return its content"""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
    return ""

def save_text_file(file_path, content):
    """Save content to a text file"""
    try:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        st.error(f"Error saving {file_path}: {e}")
        return False

def parse_userbrief(content):
    """Parse userbrief content and extract preferences"""
    preferences = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('📌'):
            # Extract preference text (remove emoji and dash)
            pref_text = line[2:].strip()
            if pref_text.startswith('- '):
                pref_text = pref_text[2:].strip()
            preferences.append({
                'id': i,
                'text': pref_text,
                'line_number': i
            })
    return preferences

def update_userbrief_preferences(content, preferences):
    """Update userbrief content with modified preferences"""
    lines = content.split('\n')
    
    # Remove old preference lines
    lines = [line for line in lines if not line.strip().startswith('📌')]
    
    # Add updated preferences
    for pref in preferences:
        lines.append(f"📌 - {pref['text']}")
    
    return '\n'.join(lines)

# File paths
memory_paths = {
    'userbrief': Path('.cursor/memory-bank/userbrief.md'),
    'long_term_memory': Path('.cursor/memory-bank/long_term_memory.json'),
    'project_brief': Path('.cursor/memory-bank/context/projectBrief.md'),
    'tech_context': Path('.cursor/memory-bank/context/techContext.md')
}

# Tabs for different memory types
tab1, tab2, tab3, tab4 = st.tabs(["📝 Requêtes", "🧠 Long-term Memory", "📋 Project Brief", "⚙️ Tech Context"])

# Tab 1: Requêtes (All userbrief entries)
with tab1:
    st.header("📝 Gestion des Requêtes")
    st.markdown("Gérez tous les éléments du userbrief : requêtes actives, préférences et archives.")
    
    userbrief_content = load_text_file(memory_paths['userbrief'])
    
    if userbrief_content:
        # Parse all userbrief entries
        lines = userbrief_content.split('\n')
        active_requests = []
        preferences = []
        archived_entries = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith('#'):
                if line.startswith('🗄️'):
                    # Active request
                    if ' - ' in line:
                        text = line.split(' - ', 1)[1]
                        active_requests.append({
                            'line_number': i,
                            'text': text,
                            'full_line': line,
                            'type': 'active'
                        })
                elif line.startswith('📌'):
                    # Preference
                    if ' - ' in line:
                        text = line.split(' - ', 1)[1]
                        preferences.append({
                            'line_number': i,
                            'text': text,
                            'full_line': line,
                            'type': 'preference'
                        })
                elif line.startswith('🧠'):
                    # Archived
                    if ' - ' in line:
                        text = line.split(' - ', 1)[1]
                        archived_entries.append({
                            'line_number': i,
                            'text': text,
                            'full_line': line,
                            'type': 'archived'
                        })
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🗄️ Requêtes Actives", len(active_requests))
        with col2:
            st.metric("📌 Préférences", len(preferences))
        with col3:
            st.metric("🧠 Archives", len(archived_entries))
        
        st.markdown("---")
        
        # Active Requests Section
        if active_requests:
            st.subheader(f"🗄️ Requêtes Actives ({len(active_requests)})")
            for i, entry in enumerate(active_requests):
                with st.expander(f"Requête #{i+1}", expanded=False):
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.write(entry['text'])
                    
                    with col2:
                        if st.button(f"🗑️", key=f"active_delete_{i}", help="Supprimer cette requête"):
                            # Remove entry and auto-save
                            updated_lines = [line for line in lines if line.strip() != entry['full_line']]
                            updated_content = '\n'.join(updated_lines)
                            if save_text_file(memory_paths['userbrief'], updated_content):
                                st.success("Requête supprimée!")
                                st.rerun()
        
        # Preferences Section
        if preferences:
            st.subheader(f"📌 Préférences ({len(preferences)})")
            for i, entry in enumerate(preferences):
                with st.expander(f"Préférence #{i+1}", expanded=False):
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.write(entry['text'])
                    
                    with col2:
                        if st.button(f"🗑️", key=f"pref_delete_{i}", help="Supprimer cette préférence"):
                            # Remove entry and auto-save
                            updated_lines = [line for line in lines if line.strip() != entry['full_line']]
                            updated_content = '\n'.join(updated_lines)
                            if save_text_file(memory_paths['userbrief'], updated_content):
                                st.success("Préférence supprimée!")
                                st.rerun()
        
        # Archived Section
        if archived_entries:
            st.subheader(f"🧠 Archives ({len(archived_entries)})")
            for i, entry in enumerate(archived_entries):
                with st.expander(f"Archive #{i+1}", expanded=False):
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.write(entry['text'])
                    
                    with col2:
                        if st.button(f"🗑️", key=f"archive_delete_{i}", help="Supprimer cette archive"):
                            # Remove entry and auto-save
                            updated_lines = [line for line in lines if line.strip() != entry['full_line']]
                            updated_content = '\n'.join(updated_lines)
                            if save_text_file(memory_paths['userbrief'], updated_content):
                                st.success("Archive supprimée!")
                                st.rerun()
        
        if not (active_requests or preferences or archived_entries):
            st.info("Aucune entrée trouvée dans le userbrief.")
    
    else:
        st.warning("Fichier userbrief non trouvé.")

# Tab 2: Long-term Memory
with tab2:
    st.header("🧠 Long-term Memory")
    st.markdown("Manage important memories and learnings from the project.")
    
    long_term_data = load_json_file(memory_paths['long_term_memory'])
    memories = long_term_data.get('memories', []) if long_term_data else []
    
    if memories:
        st.subheader(f"Stored Memories ({len(memories)})")
        
        # Display memories with edit/delete options
        for i, memory in enumerate(memories):
            with st.expander(f"Memory #{i+1}: {memory.get('timestamp', 'No date')}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown("**Content:**")
                    st.write(memory.get('content', 'No content'))
                    
                    # Show embedding info if available
                    if memory.get('embedding'):
                        st.markdown(f"**Embedding:** {len(memory['embedding'])} dimensions")
                
                with col2:
                    st.markdown("**Info:**")
                    st.write(f"**Date:** {memory.get('timestamp', 'Unknown')}")
                    
                    if st.button(f"🗑️ Delete", key=f"memory_delete_{i}"):
                        # Remove memory and auto-save
                        memories.pop(i)
                        updated_data = {'memories': memories}
                        if save_json_file(memory_paths['long_term_memory'], updated_data):
                            st.success("Memory deleted automatically!")
                            st.rerun()
    else:
        st.info("No long-term memories found.")
    
    # Add new memory
    st.subheader("➕ Add New Memory")
    with st.form("add_memory_form"):
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
                updated_data = {'memories': memories}
                
                if save_json_file(memory_paths['long_term_memory'], updated_data):
                    st.success("✅ New memory added!")
                    st.rerun()
            else:
                st.error("Please enter memory content.")

# Tab 3: Project Brief
with tab3:
    st.header("📋 Project Brief")
    st.markdown("Edit the main project description and objectives.")
    
    project_brief_content = load_text_file(memory_paths['project_brief'])
    
    # Edit project brief with auto-save
    updated_brief = st.text_area(
        "Project Brief Content:",
        value=project_brief_content,
        height=300,
        help="Describe your project's goals, scope, and key requirements.",
        key="project_brief_editor"
    )
    
    # Auto-save on change
    if updated_brief != project_brief_content:
        if save_text_file(memory_paths['project_brief'], updated_brief):
            st.success("✅ Project brief updated automatically!")
            st.rerun()
    
    # Clear button
    if st.button("🗑️ Clear Brief"):
        if save_text_file(memory_paths['project_brief'], ""):
            st.success("Project brief cleared!")
            st.rerun()
    
    # Show current stats
    if project_brief_content:
        st.subheader("📊 Brief Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Characters", len(project_brief_content))
        
        with col2:
            word_count = len(project_brief_content.split())
            st.metric("Words", word_count)
        
        with col3:
            line_count = len(project_brief_content.split('\n'))
            st.metric("Lines", line_count)

# Tab 4: Tech Context
with tab4:
    st.header("⚙️ Technical Context")
    st.markdown("Manage technical specifications, architecture, and constraints.")
    
    tech_context_content = load_text_file(memory_paths['tech_context'])
    
    # Edit tech context with auto-save
    updated_context = st.text_area(
        "Technical Context Content:",
        value=tech_context_content,
        height=300,
        help="Describe technical architecture, frameworks, constraints, and requirements.",
        key="tech_context_editor"
    )
    
    # Auto-save on change
    if updated_context != tech_context_content:
        if save_text_file(memory_paths['tech_context'], updated_context):
            st.success("✅ Technical context updated automatically!")
            st.rerun()
    
    # Clear button
    if st.button("🗑️ Clear Context"):
        if save_text_file(memory_paths['tech_context'], ""):
            st.success("Technical context cleared!")
            st.rerun()
    
    # Show current stats
    if tech_context_content:
        st.subheader("📊 Context Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Characters", len(tech_context_content))
        
        with col2:
            word_count = len(tech_context_content.split())
            st.metric("Words", word_count)
        
        with col3:
            line_count = len(tech_context_content.split('\n'))
            st.metric("Lines", line_count)



# Sidebar: Memory Overview
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Memory Overview")

# Count items in each category
userbrief_content = load_text_file(memory_paths['userbrief'])
preferences_count = len(parse_userbrief(userbrief_content)) if userbrief_content else 0

long_term_data = load_json_file(memory_paths['long_term_memory'])
memories_count = len(long_term_data.get('memories', [])) if long_term_data else 0

project_brief_exists = memory_paths['project_brief'].exists() and len(load_text_file(memory_paths['project_brief'])) > 0
tech_context_exists = memory_paths['tech_context'].exists() and len(load_text_file(memory_paths['tech_context'])) > 0

st.sidebar.metric("📌 Preferences", preferences_count)
st.sidebar.metric("🧠 Memories", memories_count)
st.sidebar.metric("📋 Project Brief", "✅" if project_brief_exists else "❌")
st.sidebar.metric("⚙️ Tech Context", "✅" if tech_context_exists else "❌")



# Help section
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Help")
st.sidebar.info("""
**Memory Types:**
- **Preferences**: Personal settings and approaches
- **Long-term**: Important learnings and insights  
- **Project Brief**: Main project description
- **Tech Context**: Technical specifications

All changes are saved immediately to the memory bank files.
""") 