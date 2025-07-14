"""
Memory data management utilities.
Handles data processing, filtering, and management for memories and requests.
"""

import json
from pathlib import Path
from datetime import datetime
from . import file_operations
load_json_file = file_operations.load_json_file
save_json_file = file_operations.save_json_file


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
        memory_paths = {
            'long_term_memory': Path('.cursor/memory-bank/workflow/long_term_memory.json')
        }
        
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
        import streamlit as st
        st.error(f"Error saving long-term memories: {e}")
        return False


def fuzzy_search_memories(memories, query):
    """Filter memories based on a fuzzy search query in their content"""
    if not query:
        return memories
    
    query = query.lower()
    
    # Simple search: check if query is a substring of content
    return [mem for mem in memories if query in mem.get('content', '').lower()]


def get_agent_memories(limit=10):
    """Get agent memories from various locations"""
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
                import streamlit as st
                st.error(f"Error reading memories from {memory_file}: {e}")
    
    return []


def get_recent_requests(limit=5):
    """Get recent requests categorized by status"""
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
        import streamlit as st
        st.error(f"Error reading userbrief: {e}")
        return {}


def process_long_term_memories(long_term_data):
    """Process and validate long-term memory data"""
    # Handle both list and dictionary formats for backward compatibility
    if long_term_data is None:
        memories = []
    elif isinstance(long_term_data, list):
        # If data is already a list, use it directly but filter out invalid entries
        memories = [mem for mem in long_term_data if isinstance(mem, dict)]
        if len(memories) < len(long_term_data):
            import streamlit as st
            st.warning(f"⚠️ Filtered out {len(long_term_data) - len(memories)} invalid memory entries.")
    elif isinstance(long_term_data, dict):
        # If data is a dictionary, extract memories array and filter
        raw_memories = long_term_data.get('memories', [])
        memories = [mem for mem in raw_memories if isinstance(mem, dict)]
        if len(memories) < len(raw_memories):
            import streamlit as st
            st.warning(f"⚠️ Filtered out {len(raw_memories) - len(memories)} invalid memory entries.")
    else:
        # Fallback for unexpected data types
        import streamlit as st
        st.error("⚠️ Unexpected long-term memory data format. Using empty list.")
        memories = []
    
    # Sort memories by timestamp (most recent first)
    memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return memories


def update_request_status(userbrief_data, req_id, new_status, comment=""):
    """Update request status with history tracking"""
    requests = userbrief_data.get('requests', [])
    
    for req in requests:
        if req.get('id') == req_id:
            req['status'] = new_status
            req['updated_at'] = datetime.now().isoformat()
            
            if 'history' not in req:
                req['history'] = []
            
            req['history'].append({
                'timestamp': datetime.now().isoformat(),
                'action': f'status_update_to_{new_status}',
                'comment': comment or f'Status changed to {new_status}'
            })
            
            return True
    
    return False 