"""
Request management utilities for the Streamlit app.
Handles creation, update, deletion and retrieval of user requests.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from PIL import Image, ImageGrab
import uuid
import streamlit as st


def get_next_request_id():
    """Get the next available request ID from userbrief.json"""
    userbrief_file = Path(".cursor/memory-bank/workflow/userbrief.json")
    if userbrief_file.exists():
        with open(userbrief_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("last_id", 0) + 1
    return 1


def save_uploaded_image(uploaded_file, request_id):
    """Save uploaded image to a structured directory and return metadata."""
    if uploaded_file is not None:
        try:
            # Create a unique filename to avoid collisions
            ext = os.path.splitext(uploaded_file.name)[1]
            unique_filename = f"req_{request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
            
            # Define save path
            save_dir = Path(".cursor/temp/images")
            save_dir.mkdir(parents=True, exist_ok=True)
            image_path = save_dir / unique_filename
            
            # Save the file
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Get image dimensions
            with Image.open(image_path) as img:
                width, height = img.size
            
            # Return image metadata
            return {
                "path": str(image_path),
                "filename": unique_filename,
                "size": uploaded_file.size,
                "width": width,
                "height": height,
                "content_type": uploaded_file.type
            }
        except Exception as e:
            st.error(f"Error saving image: {e}")
            return None
    return None


def get_image_from_clipboard():
    """Attempt to get an image from the clipboard."""
    try:
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            return image
    except Exception:
        # Silently ignore errors, as this can fail on some OS
        # if the clipboard is empty or doesn't contain an image.
        pass
    return None


def save_pasted_image(image: Image.Image, request_id: int):
    """Save a pasted image from clipboard to a structured directory and return metadata."""
    if image:
        try:
            # Create a unique filename
            unique_filename = f"req_{request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_pasted.png"
            
            # Define save path
            save_dir = Path(".cursor/temp/images")
            save_dir.mkdir(parents=True, exist_ok=True)
            image_path = save_dir / unique_filename
            
            # Save the image as PNG
            image.save(image_path, "PNG")

            # Get image metadata
            width, height = image.size
            size = os.path.getsize(image_path)
            
            return {
                "path": str(image_path),
                "filename": unique_filename,
                "size": size,
                "width": width,
                "height": height,
                "content_type": "image/png"
            }
        except Exception as e:
            st.error(f"Error saving pasted image: {e}")
            return None
    return None


def create_new_request(content: str, image_metadata: Optional[Dict] = None):
    """Create a new request in userbrief.json, with optional image attachment."""
    try:
        userbrief_file = Path(".cursor/memory-bank/workflow/userbrief.json")
        
        if userbrief_file.exists():
            with open(userbrief_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"version": "1.0.0", "last_id": 0, "requests": []}

        new_id = data.get("last_id", 0) + 1
        timestamp = datetime.now().isoformat()
        
        new_req = {
            "id": new_id,
            "content": content,
            "status": "new",
            "image": image_metadata, # Can be None
            "created_at": timestamp,
            "updated_at": timestamp,
            "history": [{
                "timestamp": timestamp,
                "action": "created",
                "comment": "Request created via Streamlit app."
            }]
        }

        data["requests"].append(new_req)
        data["last_id"] = new_id

        with open(userbrief_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"Error creating request: {e}")
        return False


def get_user_request(request_id: int) -> Optional[Dict]:
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
                req["history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "updated",
                    "comment": "Request content updated via Streamlit app."
                })
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