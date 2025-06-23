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

def save_long_term_memories(memories):
    """Save long-term memories in the correct format based on existing file structure"""
    try:
        # Check current file format to maintain consistency
        existing_data = load_json_file(memory_paths['long_term_memory'])
        
        if existing_data is None or isinstance(existing_data, list):
            # Save as list format (current format)
            data_to_save = memories
        else:
            # Save as dictionary format
            data_to_save = {'memories': memories}
        
        return save_json_file(memory_paths['long_term_memory'], data_to_save)
    except Exception as e:
        st.error(f"Error saving long-term memories: {e}")
        return False

# File paths
memory_paths = {
    'userbrief': Path('.cursor/memory-bank/workflow/userbrief.json'),
    'long_term_memory': Path('.cursor/memory-bank/workflow/long_term_memory.json'),
    'project_brief': Path('.cursor/memory-bank/context/projectBrief.md'),
    'tech_context': Path('.cursor/memory-bank/context/techContext.md')
}

# Tabs for different memory types
tab1, tab2, tab3, tab4 = st.tabs(["📝 Requêtes", "🧠 Long-term Memory", "📋 Project Brief", "⚙️ Tech Context"])

# Tab 1: Requêtes (All userbrief entries from JSON)
with tab1:
    st.header("📝 Gestion des Requêtes")
    st.markdown("Gérez toutes les requêtes du nouveau système JSON avec statuts structurés.")
    
    userbrief_data = load_json_file(memory_paths['userbrief'])
    
    if userbrief_data:
        requests = userbrief_data.get("requests", [])
        
        if requests:
            # Count by status
            new_requests = [req for req in requests if req.get("status") == "new"]
            in_progress_requests = [req for req in requests if req.get("status") == "in_progress"]
            archived_requests = [req for req in requests if req.get("status") == "archived"]
            
            # Display statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total", len(requests))
            with col2:
                st.metric("🆕 Nouvelles", len(new_requests))
            with col3:
                st.metric("⚡ En cours", len(in_progress_requests))
            with col4:
                st.metric("✅ Archivées", len(archived_requests))
            
            st.markdown("---")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                show_new = st.checkbox("Afficher Nouvelles (🆕)", value=True)
            with col2:
                show_in_progress = st.checkbox("Afficher En cours (⚡)", value=True)
            with col3:
                show_archived = st.checkbox("Afficher Archivées (✅)", value=False)
            
            # Filter and sort requests
            filtered_requests = []
            for req in requests:
                status = req.get('status', 'unknown')
                if (status == 'new' and show_new) or \
                   (status == 'in_progress' and show_in_progress) or \
                   (status == 'archived' and show_archived):
                    filtered_requests.append(req)
            
            # Sort by most recent first
            filtered_requests.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            if filtered_requests:
                st.info(f"Affichage de {len(filtered_requests)} requête(s) sur {len(requests)} au total")
                
                # Display requests
                for req in filtered_requests:
                    status = req.get('status', 'unknown')
                    status_emoji = {'new': '🆕', 'in_progress': '⚡', 'archived': '✅'}.get(status, '❓')
                    
                    with st.expander(f"{status_emoji} #{req.get('id', 'N/A')}: {req.get('content', '')[:80]}...", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown("**Contenu:**")
                            st.write(req.get('content', 'Pas de contenu'))
                            
                            st.markdown("**Informations:**")
                            st.write(f"**Statut:** {status.title()}")
                            st.write(f"**Créé:** {req.get('created_at', 'Inconnu')[:19].replace('T', ' ')}")
                            st.write(f"**Modifié:** {req.get('updated_at', 'Inconnu')[:19].replace('T', ' ')}")
                            
                            # Show history if available
                            history = req.get('history', [])
                            if history:
                                st.markdown("**Historique:**")
                                for entry in history[-3:]:  # Show last 3 entries
                                    timestamp = entry.get('timestamp', 'Inconnu')[:19].replace('T', ' ')
                                    action = entry.get('action', 'Inconnu')
                                    comment = entry.get('comment', 'Pas de commentaire')
                                    st.write(f"- {timestamp}: **{action}** - {comment}")
                        
                        with col2:
                            st.markdown("**Actions:**")
                            
                            # Enhanced action buttons with simulated functionality
                            req_id = req.get('id')
                            
                            if status == 'new':
                                if st.button(f"⚡ En cours", key=f"progress_{req_id}", help="Marquer comme en cours"):
                                    # Simulate status update
                                    req['status'] = 'in_progress'
                                    req['updated_at'] = datetime.now().isoformat()
                                    if 'history' not in req:
                                        req['history'] = []
                                    req['history'].append({
                                        'timestamp': datetime.now().isoformat(),
                                        'action': 'status_update',
                                        'comment': 'Marked as in progress via Memory Management interface'
                                    })
                                    
                                    # Save updated userbrief
                                    if save_json_file(memory_paths['userbrief'], userbrief_data):
                                        st.success(f"✅ Requête #{req_id} marquée comme en cours!")
                                        st.toast(f"⚡ Request #{req_id} marked as in progress", icon="⚡")
                                        st.rerun()
                                
                                if st.button(f"✅ Archiver", key=f"archive_new_{req_id}", help="Marquer comme archivée"):
                                    # Simulate archiving
                                    req['status'] = 'archived'
                                    req['updated_at'] = datetime.now().isoformat()
                                    if 'history' not in req:
                                        req['history'] = []
                                    req['history'].append({
                                        'timestamp': datetime.now().isoformat(),
                                        'action': 'mark_archived',
                                        'comment': 'Manually archived via Memory Management interface'
                                    })
                                    
                                    # Save updated userbrief
                                    if save_json_file(memory_paths['userbrief'], userbrief_data):
                                        st.success(f"✅ Requête #{req_id} archivée!")
                                        st.toast(f"✅ Request #{req_id} archived successfully", icon="✅")
                                        st.rerun()
                            
                            elif status == 'in_progress':
                                if st.button(f"✅ Archiver", key=f"archive_progress_{req_id}", help="Marquer comme archivée"):
                                    # Simulate archiving
                                    req['status'] = 'archived'
                                    req['updated_at'] = datetime.now().isoformat()
                                    if 'history' not in req:
                                        req['history'] = []
                                    req['history'].append({
                                        'timestamp': datetime.now().isoformat(),
                                        'action': 'mark_archived',
                                        'comment': 'Manually archived via Memory Management interface'
                                    })
                                    
                                    # Save updated userbrief
                                    if save_json_file(memory_paths['userbrief'], userbrief_data):
                                        st.success(f"✅ Requête #{req_id} archivée!")
                                        st.toast(f"✅ Request #{req_id} archived successfully", icon="✅")
                                        st.rerun()
                                
                                if st.button(f"🔄 Retour nouveau", key=f"back_new_{req_id}", help="Remettre en statut nouveau"):
                                    # Simulate status rollback
                                    req['status'] = 'new'
                                    req['updated_at'] = datetime.now().isoformat()
                                    if 'history' not in req:
                                        req['history'] = []
                                    req['history'].append({
                                        'timestamp': datetime.now().isoformat(),
                                        'action': 'status_update',
                                        'comment': 'Reset to new status via Memory Management interface'
                                    })
                                    
                                    # Save updated userbrief
                                    if save_json_file(memory_paths['userbrief'], userbrief_data):
                                        st.success(f"✅ Requête #{req_id} remise en statut nouveau!")
                                        st.rerun()
                            
                            elif status == 'archived':
                                if st.button(f"🔄 Réactiver", key=f"reactivate_{req_id}", help="Remettre en statut nouveau"):
                                    # Simulate reactivation
                                    req['status'] = 'new'
                                    req['updated_at'] = datetime.now().isoformat()
                                    if 'history' not in req:
                                        req['history'] = []
                                    req['history'].append({
                                        'timestamp': datetime.now().isoformat(),
                                        'action': 'reactivate',
                                        'comment': 'Reactivated from archived status via Memory Management interface'
                                    })
                                    
                                    # Save updated userbrief
                                    if save_json_file(memory_paths['userbrief'], userbrief_data):
                                        st.success(f"✅ Requête #{req_id} réactivée!")
                                        st.toast(f"🔄 Request #{req_id} reactivated", icon="🔄")
                                        st.rerun()
                                
                                st.caption("*Requête archivée*")
            else:
                st.info("Aucune requête ne correspond aux filtres sélectionnés.")
        else:
            st.info("Aucune requête trouvée dans le fichier JSON.")
    else:
        st.warning("Fichier userbrief JSON non trouvé.")
    
    # Information about the new system
    st.markdown("---")
    st.subheader("ℹ️ À propos du nouveau système")
    st.info("""
    **Système de statuts des requêtes:**
    - **Nouvelles (🆕)**: Requêtes en attente de traitement par le workflow de l'agent
    - **En cours (⚡)**: Requêtes actuellement en cours de traitement
    - **Archivées (✅)**: Requêtes terminées avec commentaires de résolution
    
    Pour ajouter de nouvelles requêtes, utilisez la page "Add New Request". Les requêtes sont maintenant gérées via un système JSON structuré qui s'intègre avec les outils MCP (Model Context Protocol).
    """)

# Tab 2: Long-term Memory
with tab2:
    st.header("🧠 Long-term Memory")
    st.markdown("Manage important memories and learnings from the project.")
    
    long_term_data = load_json_file(memory_paths['long_term_memory'])
    
    # Handle both list and dictionary formats for backward compatibility
    if long_term_data is None:
        memories = []
    elif isinstance(long_term_data, list):
        # If data is already a list, use it directly
        memories = long_term_data
    elif isinstance(long_term_data, dict):
        # If data is a dictionary, extract memories array
        memories = long_term_data.get('memories', [])
    else:
        # Fallback for unexpected data types
        st.error("⚠️ Unexpected long-term memory data format. Using empty list.")
        memories = []
    
    if memories:
        st.subheader(f"Stored Memories ({len(memories)})")
        
        # Display memories directly without accordions
        for i, memory in enumerate(memories):
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
                                memories[i]['content'] = new_content
                                memories[i]['timestamp'] = datetime.now().isoformat()  # Update timestamp
                                updated_data = {'memories': memories}
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
                        memories.pop(i)
                        if save_long_term_memories(memories):
                            st.success("Memory deleted!")
                            st.rerun()
                
                # Add visual separator between memories
                st.markdown("---")
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
                
                if save_long_term_memories(memories):
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
# Handle both list and dictionary formats for backward compatibility
if long_term_data:
    if isinstance(long_term_data, list):
        memories_count = len(long_term_data)
    elif isinstance(long_term_data, dict):
        memories_count = len(long_term_data.get('memories', []))
    else:
        memories_count = 0
else:
    memories_count = 0

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