"""
Request display management utilities.
Handles the display and interaction with user requests in different categories.
"""

import streamlit as st
from datetime import datetime
import file_operations
import memory_data_manager
save_json_file = file_operations.save_json_file
get_memory_file_paths = file_operations.get_memory_file_paths
update_request_status = memory_data_manager.update_request_status


def display_request_statistics(requests):
    """Display request statistics in columns"""
    new_requests = [req for req in requests if req.get("status") == "new"]
    in_progress_requests = [req for req in requests if req.get("status") == "in_progress"]
    archived_requests = [req for req in requests if req.get("status") == "archived"]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total", len(requests))
    with col2:
        st.metric("🆕 Nouvelles", len(new_requests))
    with col3:
        st.metric("⚡ En cours", len(in_progress_requests))
    with col4:
        st.metric("✅ Archivées", len(archived_requests))
    
    return new_requests, in_progress_requests, archived_requests


def display_filter_options():
    """Display filter options for request display"""
    st.subheader("🔍 Filter & Display Options")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        show_new = st.checkbox("🆕 Nouvelles", value=True)
    with col2:
        show_in_progress = st.checkbox("⚡ En cours", value=True)
    with col3:
        show_archived = st.checkbox("✅ Archivées", value=False)
    with col4:
        show_full_content = st.checkbox("📄 Contenu complet", value=True, help="Afficher le contenu complet au lieu du résumé")
    
    return show_new, show_in_progress, show_archived, show_full_content


def display_request_content(req, show_full_content):
    """Display request content with full or preview mode"""
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


def display_request_metadata(req):
    """Display request metadata in columns"""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"🕐 **Créé:** {req.get('created_at', 'Inconnu')[:19].replace('T', ' ')}")
    with col2:
        st.caption(f"🔄 **Modifié:** {req.get('updated_at', 'Inconnu')[:19].replace('T', ' ')}")
    with col3:
        status_text = {
            'new': 'Nouvelle',
            'in_progress': 'En cours',
            'archived': 'Archivée'
        }.get(req.get('status'), 'Inconnu')
        st.caption(f"🏷️ **Statut:** {status_text}")


def display_request_history(req):
    """Display request history if available"""
    history = req.get('history', [])
    if history:
        with st.expander("📋 Historique récent", expanded=False):
            for entry in history[-3:]:
                timestamp = entry.get('timestamp', 'Inconnu')[:19].replace('T', ' ')
                action = entry.get('action', 'Inconnu')
                comment = entry.get('comment', 'Pas de commentaire')
                st.write(f"• **{timestamp}** - {action}: {comment}")


def handle_request_status_change(userbrief_data, req_id, new_status, comment):
    """Handle request status change with data persistence"""
    memory_paths = get_memory_file_paths()
    
    if update_request_status(userbrief_data, req_id, new_status, comment):
        if save_json_file(memory_paths['userbrief'], userbrief_data):
            return True
    return False


def display_in_progress_requests(in_progress_requests, userbrief_data, show_full_content):
    """Display in-progress requests with action buttons"""
    if not in_progress_requests:
        return
    
    st.header("⚡ Requêtes en cours")
    st.success(f"🔥 {len(in_progress_requests)} requête(s) actuellement en traitement")
    
    for req in in_progress_requests:
        req_id = req.get('id')
        
        with st.container():
            st.markdown(f"### ⚡ Requête #{req_id} - En cours")
            
            # Content display
            display_request_content(req, show_full_content)
            
            # Metadata
            display_request_metadata(req)
            
            # Actions
            col_actions1, col_actions2 = st.columns(2)
            with col_actions1:
                if st.button(f"✅ Archiver", key=f"archive_progress_{req_id}", help="Marquer comme archivée"):
                    if handle_request_status_change(userbrief_data, req_id, 'archived', 'Manually archived via Memory Management interface'):
                        st.success(f"✅ Requête #{req_id} archivée!")
                        st.toast(f"✅ Request #{req_id} archived successfully", icon="✅")
                        st.rerun()
            
            with col_actions2:
                if st.button(f"🔄 Retour nouveau", key=f"back_new_{req_id}", help="Remettre en statut nouveau"):
                    if handle_request_status_change(userbrief_data, req_id, 'new', 'Reset to new status via Memory Management interface'):
                        st.success(f"✅ Requête #{req_id} remise en statut nouveau!")
                        st.rerun()
            
            # Show history
            display_request_history(req)
            st.markdown("---")


def display_new_requests(new_requests, userbrief_data, show_full_content):
    """Display new requests with action buttons"""
    if not new_requests:
        return
    
    st.header("🆕 Nouvelles requêtes")
    st.info(f"📊 {len(new_requests)} nouvelle(s) requête(s) en attente de traitement")
    
    for req in new_requests:
        req_id = req.get('id')
        
        with st.container():
            st.markdown(f"### 🆕 Requête #{req_id} - Nouvelle")
            
            # Content display
            display_request_content(req, show_full_content)
            
            # Metadata
            display_request_metadata(req)
            
            # Actions
            col_actions1, col_actions2 = st.columns(2)
            with col_actions1:
                if st.button(f"⚡ En cours", key=f"progress_{req_id}", help="Marquer comme en cours"):
                    if handle_request_status_change(userbrief_data, req_id, 'in_progress', 'Marked as in progress via Memory Management interface'):
                        st.success(f"✅ Requête #{req_id} marquée comme en cours!")
                        st.toast(f"⚡ Request #{req_id} marked as in progress", icon="⚡")
                        st.rerun()
            
            with col_actions2:
                if st.button(f"✅ Archiver", key=f"archive_new_{req_id}", help="Marquer comme archivée"):
                    if handle_request_status_change(userbrief_data, req_id, 'archived', 'Manually archived via Memory Management interface'):
                        st.success(f"✅ Requête #{req_id} archivée!")
                        st.toast(f"✅ Request #{req_id} archived successfully", icon="✅")
                        st.rerun()
            
            st.markdown("---")


def display_archived_requests(archived_requests, userbrief_data, show_full_content):
    """Display archived requests with reactivation option"""
    if not archived_requests:
        return
    
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
            display_request_content(req, show_full_content)
            
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
                if handle_request_status_change(userbrief_data, req_id, 'new', 'Reactivated from archived status via Memory Management interface'):
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


def display_request_system_info():
    """Display information about the request system"""
    st.markdown("---")
    st.subheader("ℹ️ À propos du nouveau système")
    st.info("""
    **Système de statuts des requêtes:**
    - **Nouvelles (🆕)**: Requêtes en attente de traitement par le workflow de l'agent
    - **En cours (⚡)**: Requêtes actuellement en cours de traitement
    - **Archivées (✅)**: Requêtes terminées avec commentaires de résolution
    
    Pour ajouter de nouvelles requêtes, utilisez la page "Add New Request". Les requêtes sont maintenant gérées via un système JSON structuré qui s'intègre avec les outils MCP (Model Context Protocol).
    """) 