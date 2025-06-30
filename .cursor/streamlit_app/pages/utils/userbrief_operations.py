"""
Userbrief operations utilities.
Handles operations on user requests from userbrief.json.
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path


def get_userbrief_requests():
    """Get unprocessed userbrief requests"""
    userbrief_file = Path('.cursor/memory-bank/workflow/userbrief.json')
    if not userbrief_file.exists():
        return []
    
    try:
        with open(userbrief_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        requests = data.get('requests', [])
        # Return only unprocessed requests (new or in_progress)
        unprocessed = [req for req in requests if req.get('status') in ['new', 'in_progress']]
        return unprocessed
    except Exception as e:
        st.error(f"Error reading userbrief: {e}")
        return []


def get_user_request(request_id: int):
    """Get a specific user request by its ID."""
    userbrief_file = Path(".cursor/memory-bank/workflow/userbrief.json")
    if not userbrief_file.exists():
        return None
    with open(userbrief_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for req in data.get("requests", []):
        if req.get("id") == request_id:
            return req
    return None


def delete_user_request(request_id: int) -> bool:
    """Deletes a user request from userbrief.json."""
    try:
        userbrief_file = Path(".cursor/memory-bank/workflow/userbrief.json")
        if not userbrief_file.exists():
            return False

        with open(userbrief_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        original_count = len(data.get("requests", []))
        data["requests"] = [req for req in data["requests"] if req.get("id") != request_id]
        
        if len(data["requests"]) < original_count:
            with open(userbrief_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        return False # Request not found
    except Exception as e:
        st.error(f"Error deleting request: {e}")
        return False


def update_user_request(request_id: int, new_content: str) -> bool:
    """Updates the content of a user request."""
    try:
        userbrief_file = Path(".cursor/memory-bank/workflow/userbrief.json")
        if not userbrief_file.exists():
            return False

        with open(userbrief_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        request_found = False
        for req in data.get("requests", []):
            if req.get("id") == request_id:
                req["content"] = new_content
                req["updated_at"] = datetime.now().isoformat()
                request_found = True
                break
        
        if request_found:
            with open(userbrief_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        return False # Request not found
    except Exception as e:
        st.error(f"Error updating request: {e}")
        return False


def create_new_request(content: str) -> bool:
    """Creates a new user request in userbrief.json."""
    try:
        userbrief_file = Path(".cursor/memory-bank/workflow/userbrief.json")
        
        # Initialize a new file if it doesn't exist
        if not userbrief_file.exists():
            data = {"version": "1.0.0", "last_id": 0, "requests": []}
        else:
            with open(userbrief_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

        # Generate new ID and create the request object
        new_id = data.get("last_id", 0) + 1
        now_iso = datetime.now().isoformat()
        
        new_request = {
            "id": new_id,
            "content": content,
            "status": "new",
            "image": None,
            "created_at": now_iso,
            "updated_at": now_iso,
            "history": [
                {
                    "timestamp": now_iso,
                    "action": "created",
                    "comment": "Request created via Memory Management interface (feedback on archived request)."
                }
            ]
        }
        
        # Append new request and update last_id
        data.get("requests", []).append(new_request)
        data["last_id"] = new_id
        
        # Save the updated data
        with open(userbrief_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        return True
    except Exception as e:
        st.error(f"Error creating new request: {e}")
        return False 