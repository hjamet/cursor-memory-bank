import streamlit as st
import sys
from pathlib import Path

# Add the parent directory of the pages directory to the path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from components.sidebar import display_sidebar

# Import the new modular utilities with absolute paths
current_dir = Path(__file__).resolve().parent
utils_dir = current_dir / "utils"
sys.path.insert(0, str(utils_dir))

import file_operations
import memory_data_manager
import memory_ui_components
import request_display_manager

# Import specific functions
load_json_file = file_operations.load_json_file
load_text_file = file_operations.load_text_file
save_text_file = file_operations.save_text_file
get_memory_file_paths = file_operations.get_memory_file_paths

get_agent_memories = memory_data_manager.get_agent_memories
process_long_term_memories = memory_data_manager.process_long_term_memories

display_agent_memory_timeline = memory_ui_components.display_agent_memory_timeline
display_long_term_memories = memory_ui_components.display_long_term_memories
display_memory_search_bar = memory_ui_components.display_memory_search_bar
display_add_memory_form = memory_ui_components.display_add_memory_form
display_text_editor_tab = memory_ui_components.display_text_editor_tab

display_request_statistics = request_display_manager.display_request_statistics
display_filter_options = request_display_manager.display_filter_options
display_in_progress_requests = request_display_manager.display_in_progress_requests
display_new_requests = request_display_manager.display_new_requests
display_archived_requests = request_display_manager.display_archived_requests
display_request_system_info = request_display_manager.display_request_system_info

st.set_page_config(page_title="Memory Management", page_icon="🧠")

display_sidebar()

st.markdown("# 🧠 Memory Management")
st.markdown("Manage your project's memory: preferences, long-term memories, project brief, and technical context.")

# Get file paths
memory_paths = get_memory_file_paths()

# Tabs for different memory types
 tab5, tab1, tab2, tab3 = st.tabs(["🤖 Agent Timeline", "📝 Requêtes", "🧠 Long-term Memory", "📖 Project Context (README.md)"])

# Tab 5: Agent Timeline
with tab5:
    st.header("🧠 Agent Memory Timeline")
    agent_memories = get_agent_memories(10)
    display_agent_memory_timeline(agent_memories)

# Tab 1: Requêtes (All userbrief entries from JSON)
with tab1:
    st.header("📝 Gestion des Requêtes")
    st.markdown("Gérez toutes les requêtes du nouveau système JSON avec statuts structurés.")
    
    userbrief_data = load_json_file(memory_paths['userbrief'])
    
    if userbrief_data:
        requests = userbrief_data.get("requests", [])
        
        if requests:
            # Display statistics and get categorized requests
            new_requests, in_progress_requests, archived_requests = display_request_statistics(requests)
            
            st.markdown("---")
            
            # Display filter options
            show_new, show_in_progress, show_archived, show_full_content = display_filter_options()
            
            st.markdown("---")
            
            # Sort all requests by updated_at (most recent first)
            new_requests.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            in_progress_requests.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            archived_requests.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            # Display requests based on filters
            if show_in_progress:
                display_in_progress_requests(in_progress_requests, userbrief_data, show_full_content)
            
            if show_new:
                display_new_requests(new_requests, userbrief_data, show_full_content)
            
            if show_archived:
                display_archived_requests(archived_requests, userbrief_data, show_full_content)
            
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
    display_request_system_info()

# Tab 2: Long-term Memory
with tab2:
    st.header("🧠 Long-term Memory")
    st.markdown("Manage important memories and learnings from the project.")
    
    long_term_data = load_json_file(memory_paths['long_term_memory'])
    memories = process_long_term_memories(long_term_data)
    
    # Search bar
    search_query = display_memory_search_bar()
    
    # Display memories
    display_long_term_memories(memories, search_query)
    
    # Add new memory form
    display_add_memory_form(memories)
