import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory of the pages directory to the path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.sidebar import display_sidebar

st.set_page_config(page_title="Memory Management", page_icon="🧠")

display_sidebar()

st.markdown("# 🧠 Memory Management")

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

def fuzzy_search_memories(memories, query):
    """Filter memories based on a fuzzy search query in their content"""
    if not query:
        return memories
    
    query = query.lower()
    
    # Simple search: check if query is a substring of content
    return [mem for mem in memories if query in mem.get('content', '').lower()]

# --- Functions from former app.py ---
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

def get_recent_requests(limit=5):
    userbrief_file = Path('.cursor/memory-bank/workflow/userbrief.json')
    if not userbrief_file.exists():
        return {}
    
    try:
        data = load_json_file(userbrief_file)
        if not data:
            return {}
            
        requests = data.get('requests', [])
        if not requests:
            return {}
        
        # Categorize requests
        new_requests = [req for req in requests if req.get('status') == 'new']
        in_progress_requests = [req for req in requests if req.get('status') == 'in_progress']
        archived_requests = [req for req in requests if req.get('status') == 'archived']
        
        # Sort by updated_at (most recent first)
        new_requests.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        in_progress_requests.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        archived_requests.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return {
            'new': new_requests[:limit],
            'in_progress': in_progress_requests[:limit],
            'archived': archived_requests[:limit],
            'total_counts': {
                'new': len(new_requests),
                'in_progress': len(in_progress_requests),
                'archived': len(archived_requests)
            }
        }
    except Exception as e:
        st.error(f"Error reading userbrief: {e}")
        return {}
# --- End of functions from former app.py ---

# File paths
memory_paths = {
    'userbrief': Path('.cursor/memory-bank/workflow/userbrief.json'),
    'long_term_memory': Path('.cursor/memory-bank/workflow/long_term_memory.json'),
    'project_brief': Path('.cursor/memory-bank/context/projectBrief.md'),
    'tech_context': Path('.cursor/memory-bank/context/techContext.md')
}

# Tabs for different memory types
tab5, tab1, tab2, tab3, tab4 = st.tabs(["🤖 Agent Timeline", "📝 Requêtes", "🧠 Long-term Memory", "📋 Project Brief", "⚙️ Tech Context"])

# Tab 5: Agent Timeline (from former app.py)
with tab5:
    # Display Agent Memories
    st.header("🧠 Agent Memory Timeline")
    agent_memories = get_agent_memories(10)

    if agent_memories:
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

    else:
        st.info("No agent memories found. Memories will appear here as the agent works and learns.")

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
            
            # Enhanced categorized display
            st.subheader("🔍 Filter & Display Options")
            
            # Filter options with better layout
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                show_new = st.checkbox("🆕 Nouvelles", value=True)
            with col2:
                show_in_progress = st.checkbox("⚡ En cours", value=True)
            with col3:
                show_archived = st.checkbox("✅ Archivées", value=False)
            with col4:
                show_full_content = st.checkbox("📄 Contenu complet", value=True, help="Afficher le contenu complet au lieu du résumé")
            
            st.markdown("---")
            
            # Sort all requests by updated_at (most recent first)
            new_requests.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            in_progress_requests.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            archived_requests.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            # Display In Progress Requests
            if show_in_progress and in_progress_requests:
                st.header("⚡ Requêtes en cours")
                st.success(f"🔥 {len(in_progress_requests)} requête(s) actuellement en traitement")
                
                for req in in_progress_requests:
                    req_id = req.get('id')
                    status = req.get('status', 'unknown')
                    
                    with st.container():
                        st.markdown(f"### ⚡ Requête #{req_id} - En cours")
                        
                        # Content display
                        content = req.get('content', 'Pas de contenu')
                        if show_full_content:
                            st.markdown("**📝 Contenu complet:**")
                            st.write(content)
                        else:
                            st.markdown("**📝 Aperçu:**")
                            preview = content[:150] + "..." if len(content) > 150 else content
                            st.write(preview)
                            if len(content) > 150:
                                with st.expander("📖 Voir le contenu complet"):
                                    st.write(content)
                        
                        # Metadata
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.caption(f"🕐 **Créé:** {req.get('created_at', 'Inconnu')[:19].replace('T', ' ')}")
                        with col2:
                            st.caption(f"🔄 **Modifié:** {req.get('updated_at', 'Inconnu')[:19].replace('T', ' ')}")
                        with col3:
                            st.caption(f"🏷️ **Statut:** En cours")
                        
                        # Actions
                        col_actions1, col_actions2 = st.columns(2)
                        with col_actions1:
                            if st.button(f"✅ Archiver", key=f"archive_progress_{req_id}", help="Marquer comme archivée"):
                                req['status'] = 'archived'
                                req['updated_at'] = datetime.now().isoformat()
                                if 'history' not in req:
                                    req['history'] = []
                                req['history'].append({
                                    'timestamp': datetime.now().isoformat(),
                                    'action': 'mark_archived',
                                    'comment': 'Manually archived via Memory Management interface'
                                })
                                
                                if save_json_file(memory_paths['userbrief'], userbrief_data):
                                    st.success(f"✅ Requête #{req_id} archivée!")
                                    st.toast(f"✅ Request #{req_id} archived successfully", icon="✅")
                                    st.rerun()
                        
                        with col_actions2:
                            if st.button(f"🔄 Retour nouveau", key=f"back_new_{req_id}", help="Remettre en statut nouveau"):
                                req['status'] = 'new'
                                req['updated_at'] = datetime.now().isoformat()
                                if 'history' not in req:
                                    req['history'] = []
                                req['history'].append({
                                    'timestamp': datetime.now().isoformat(),
                                    'action': 'status_update',
                                    'comment': 'Reset to new status via Memory Management interface'
                                })
                                
                                if save_json_file(memory_paths['userbrief'], userbrief_data):
                                    st.success(f"✅ Requête #{req_id} remise en statut nouveau!")
                                    st.rerun()
                        
                        # Show history
                        history = req.get('history', [])
                        if history:
                            with st.expander("📋 Historique récent", expanded=False):
                                for entry in history[-3:]:
                                    timestamp = entry.get('timestamp', 'Inconnu')[:19].replace('T', ' ')
                                    action = entry.get('action', 'Inconnu')
                                    comment = entry.get('comment', 'Pas de commentaire')
                                    st.write(f"• **{timestamp}** - {action}: {comment}")
                        
                        st.markdown("---")
            
            # Display New Requests
            if show_new and new_requests:
                st.header("🆕 Nouvelles requêtes")
                st.info(f"📊 {len(new_requests)} nouvelle(s) requête(s) en attente de traitement")
                
                for req in new_requests:
                    req_id = req.get('id')
                    
                    with st.container():
                        st.markdown(f"### 🆕 Requête #{req_id} - Nouvelle")
                        
                        # Content display
                        content = req.get('content', 'Pas de contenu')
                        if show_full_content:
                            st.markdown("**📝 Contenu complet:**")
                            st.write(content)
                        else:
                            st.markdown("**📝 Aperçu:**")
                            preview = content[:150] + "..." if len(content) > 150 else content
                            st.write(preview)
                            if len(content) > 150:
                                with st.expander("📖 Voir le contenu complet"):
                                    st.write(content)
                        
                        # Metadata
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.caption(f"🕐 **Créé:** {req.get('created_at', 'Inconnu')[:19].replace('T', ' ')}")
                        with col2:
                            st.caption(f"🔄 **Modifié:** {req.get('updated_at', 'Inconnu')[:19].replace('T', ' ')}")
                        with col3:
                            st.caption(f"🏷️ **Statut:** Nouvelle")
                        
                        # Actions
                        col_actions1, col_actions2 = st.columns(2)
                        with col_actions1:
                            if st.button(f"⚡ En cours", key=f"progress_{req_id}", help="Marquer comme en cours"):
                                req['status'] = 'in_progress'
                                req['updated_at'] = datetime.now().isoformat()
                                if 'history' not in req:
                                    req['history'] = []
                                req['history'].append({
                                    'timestamp': datetime.now().isoformat(),
                                    'action': 'status_update',
                                    'comment': 'Marked as in progress via Memory Management interface'
                                })
                                
                                if save_json_file(memory_paths['userbrief'], userbrief_data):
                                    st.success(f"✅ Requête #{req_id} marquée comme en cours!")
                                    st.toast(f"⚡ Request #{req_id} marked as in progress", icon="⚡")
                                    st.rerun()
                        
                        with col_actions2:
                            if st.button(f"✅ Archiver", key=f"archive_new_{req_id}", help="Marquer comme archivée"):
                                req['status'] = 'archived'
                                req['updated_at'] = datetime.now().isoformat()
                                if 'history' not in req:
                                    req['history'] = []
                                req['history'].append({
                                    'timestamp': datetime.now().isoformat(),
                                    'action': 'mark_archived',
                                    'comment': 'Manually archived via Memory Management interface'
                                })
                                
                                if save_json_file(memory_paths['userbrief'], userbrief_data):
                                    st.success(f"✅ Requête #{req_id} archivée!")
                                    st.toast(f"✅ Request #{req_id} archived successfully", icon="✅")
                                    st.rerun()
                        
                        st.markdown("---")
            
            # Display Archived Requests
            if show_archived and archived_requests:
                st.header("✅ Requêtes archivées")
                st.info(f"📊 {len(archived_requests)} requête(s) archivée(s)")
                
                # Show only first 10 archived requests by default
                display_count = min(10, len(archived_requests))
                show_all_archived = st.checkbox(f"Afficher toutes les {len(archived_requests)} requêtes archivées", value=False)
                
                display_archived = archived_requests if show_all_archived else archived_requests[:display_count]
                
                for req in display_archived:
                    req_id = req.get('id')
                    
                    with st.container():
                        st.markdown(f"### ✅ Requête #{req_id} - Archivée")
                        
                        # Content display
                        content = req.get('content', 'Pas de contenu')
                        if show_full_content:
                            st.markdown("**📝 Contenu complet:**")
                            st.write(content)
                        else:
                            st.markdown("**📝 Aperçu:**")
                            preview = content[:150] + "..." if len(content) > 150 else content
                            st.write(preview)
                            if len(content) > 150:
                                with st.expander("📖 Voir le contenu complet"):
                                    st.write(content)
                        
                        # Metadata
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.caption(f"🕐 **Créé:** {req.get('created_at', 'Inconnu')[:19].replace('T', ' ')}")
                        with col2:
                            st.caption(f"✅ **Archivé:** {req.get('updated_at', 'Inconnu')[:19].replace('T', ' ')}")
                        with col3:
                            st.caption(f"🏷️ **Statut:** Archivée")
                        
                        # Reactivation action
                        if st.button(f"🔄 Réactiver", key=f"reactivate_{req_id}", help="Remettre en statut nouveau"):
                            req['status'] = 'new'
                            req['updated_at'] = datetime.now().isoformat()
                            if 'history' not in req:
                                req['history'] = []
                            req['history'].append({
                                'timestamp': datetime.now().isoformat(),
                                'action': 'reactivate',
                                'comment': 'Reactivated from archived status via Memory Management interface'
                            })
                            
                            if save_json_file(memory_paths['userbrief'], userbrief_data):
                                st.success(f"✅ Requête #{req_id} réactivée!")
                                st.toast(f"🔄 Request #{req_id} reactivated", icon="🔄")
                                st.rerun()
                        
                        # Show completion history
                        history = req.get('history', [])
                        if history:
                            completion_entries = [entry for entry in history if 'archive' in entry.get('action', '').lower()]
                            if completion_entries:
                                latest_completion = completion_entries[-1]
                                comment = latest_completion.get('comment', 'Request completed')
                                st.caption(f"📝 **Note de completion:** {comment}")
                        
                        st.markdown("---")
                
                if not show_all_archived and len(archived_requests) > display_count:
                    st.info(f"💡 Affichage des {display_count} requêtes archivées les plus récentes. Cochez la case ci-dessus pour voir toutes les {len(archived_requests)} requêtes.")
            
            # Summary information
            if not show_new and not show_in_progress and not show_archived:
                st.info("Sélectionnez au moins un type de requête à afficher.")
            elif not any([new_requests and show_new, in_progress_requests and show_in_progress, archived_requests and show_archived]):
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
        # If data is already a list, use it directly but filter out invalid entries
        memories = [mem for mem in long_term_data if isinstance(mem, dict)]
        if len(memories) < len(long_term_data):
            st.warning(f"⚠️ Filtered out {len(long_term_data) - len(memories)} invalid memory entries.")
    elif isinstance(long_term_data, dict):
        # If data is a dictionary, extract memories array and filter
        raw_memories = long_term_data.get('memories', [])
        memories = [mem for mem in raw_memories if isinstance(mem, dict)]
        if len(memories) < len(raw_memories):
            st.warning(f"⚠️ Filtered out {len(raw_memories) - len(memories)} invalid memory entries.")
    else:
        # Fallback for unexpected data types
        st.error("⚠️ Unexpected long-term memory data format. Using empty list.")
        memories = []
    
    # Sort memories by timestamp (most recent first)
    memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    # Search bar
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
                        # Ensure we're deleting the correct memory by checking bounds
                        if 0 <= i < len(memories):
                            memories.pop(i)
                            if save_long_term_memories(memories):
                                st.success("Memory deleted!")
                                st.rerun()
                        else:
                            st.error("Error: Invalid memory index for deletion.")
                
                # Add visual separator between memories
                st.markdown("---")
    elif search_query:
        st.warning(f"No memories found matching your search for \"{search_query}\".")
    else:
        st.info("No long-term memories found.")
    
    # Add new memory
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