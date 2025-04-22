import json
import os
from datetime import datetime
from typing import Optional, List, Tuple
from app.models.user import User
from pymongo import MongoClient
from bson.objectid import ObjectId

# Local file storage
DB_DIR = "local_db"
USERS_FILE = os.path.join(DB_DIR, "users.json")
SCREENSHOTS_FILE = os.path.join(DB_DIR, "screenshots.json")
FOLDERS_FILE = os.path.join(DB_DIR, "folders.json")
SEARCH_HISTORY_FILE = os.path.join(DB_DIR, "search_history.json")

# Ensure directory exists
os.makedirs(DB_DIR, exist_ok=True)

# Initialize files if they don't exist
for file_path in [USERS_FILE, SCREENSHOTS_FILE, FOLDERS_FILE, SEARCH_HISTORY_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)

def _read_json(file_path: str) -> list:
    with open(file_path, "r") as f:
        return json.load(f)

def _write_json(file_path: str, data: list):
    with open(file_path, "w") as f:
        json.dump(data, f)

def insert_screenshot(metadata: dict) -> str:
    """Insert a new screenshot record"""
    metadata["created_at"] = datetime.utcnow().isoformat()
    metadata["id"] = str(len(_read_json(SCREENSHOTS_FILE)) + 1)
    
    # If screenshot is added to a folder, increment folder's screenshot count
    if metadata.get("folder_id"):
        folders = _read_json(FOLDERS_FILE)
        for folder in folders:
            if folder["id"] == metadata["folder_id"]:
                folder["screenshot_count"] += 1
                break
        _write_json(FOLDERS_FILE, folders)
    
    screenshots = _read_json(SCREENSHOTS_FILE)
    screenshots.append(metadata)
    _write_json(SCREENSHOTS_FILE, screenshots)
    
    return metadata["id"]

def get_user(username: str) -> Optional[User]:
    users = _read_json(USERS_FILE)
    for user in users:
        if user["username"] == username:
            return User(**user)
    return None

def create_user(user_data: dict) -> User:
    user_data["created_at"] = datetime.utcnow().isoformat()
    user_data["id"] = str(len(_read_json(USERS_FILE)) + 1)
    
    users = _read_json(USERS_FILE)
    users.append(user_data)
    _write_json(USERS_FILE, users)
    
    # Return user without password
    user_data.pop("hashed_password")
    return User(**user_data)

def get_screenshots(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    search_term: Optional[str] = None
) -> List[dict]:
    screenshots = _read_json(SCREENSHOTS_FILE)
    filtered = [s for s in screenshots if s["user_id"] == user_id]
    
    if category:
        filtered = [s for s in filtered if s.get("category") == category]
        
    if search_term:
        search_term = search_term.lower()
        filtered = [
            s for s in filtered
            if (search_term in s["filename"].lower() or
                (s.get("description") and search_term in s["description"].lower()) or
                any(search_term in tag.lower() for tag in s.get("vision_tags", [])))
        ]
    
    return filtered[skip:skip + limit]

def get_screenshot_by_id(screenshot_id: str, user_id: str) -> Optional[dict]:
    screenshots = _read_json(SCREENSHOTS_FILE)
    for screenshot in screenshots:
        if screenshot["id"] == screenshot_id and screenshot["user_id"] == user_id:
            return screenshot
    return None

def update_screenshot(
    screenshot_id: str,
    user_id: str,
    update_data: dict
) -> bool:
    screenshots = _read_json(SCREENSHOTS_FILE)
    for i, screenshot in enumerate(screenshots):
        if screenshot["id"] == screenshot_id and screenshot["user_id"] == user_id:
            screenshots[i].update(update_data)
            _write_json(SCREENSHOTS_FILE, screenshots)
            return True
    return False

def delete_screenshot(screenshot_id: str, user_id: str) -> bool:
    screenshots = _read_json(SCREENSHOTS_FILE)
    for i, screenshot in enumerate(screenshots):
        if screenshot["id"] == screenshot_id and screenshot["user_id"] == user_id:
            del screenshots[i]
            _write_json(SCREENSHOTS_FILE, screenshots)
            return True
    return False

def get_screenshot_count(user_id: str, category: Optional[str] = None) -> int:
    screenshots = _read_json(SCREENSHOTS_FILE)
    filtered = [s for s in screenshots if s["user_id"] == user_id]
    if category:
        filtered = [s for s in filtered if s.get("category") == category]
    return len(filtered)

# Folder operations
def create_folder(folder_data: dict) -> str:
    """Create a new folder and return its ID"""
    folder_data["created_at"] = datetime.utcnow().isoformat()
    folder_data["updated_at"] = folder_data["created_at"]
    folder_data["id"] = str(len(_read_json(FOLDERS_FILE)) + 1)
    folder_data["screenshot_count"] = 0
    
    folders = _read_json(FOLDERS_FILE)
    folders.append(folder_data)
    _write_json(FOLDERS_FILE, folders)
    
    return folder_data["id"]

def get_user_folders(user_id: str, parent_id: Optional[str] = None) -> List[dict]:
    """Get all folders for a user, optionally filtered by parent folder"""
    folders = _read_json(FOLDERS_FILE)
    filtered = [f for f in folders if f["user_id"] == user_id]
    if parent_id is not None:
        filtered = [f for f in filtered if f.get("parent_id") == parent_id]
    return filtered

def update_folder(folder_id: str, user_id: str, update_data: dict) -> bool:
    """Update folder information"""
    folders = _read_json(FOLDERS_FILE)
    for i, folder in enumerate(folders):
        if folder["id"] == folder_id and folder["user_id"] == user_id:
            folders[i].update(update_data)
            folders[i]["updated_at"] = datetime.utcnow().isoformat()
            _write_json(FOLDERS_FILE, folders)
            return True
    return False

def delete_folder(folder_id: str, user_id: str) -> bool:
    """Delete a folder and update its screenshots"""
    folders = _read_json(FOLDERS_FILE)
    screenshots = _read_json(SCREENSHOTS_FILE)
    
    # Find and remove folder
    folder_index = None
    for i, folder in enumerate(folders):
        if folder["id"] == folder_id and folder["user_id"] == user_id:
            folder_index = i
            break
    
    if folder_index is None:
        return False
    
    # Remove folder
    del folders[folder_index]
    _write_json(FOLDERS_FILE, folders)
    
    # Update screenshots to remove folder reference
    for screenshot in screenshots:
        if screenshot.get("folder_id") == folder_id:
            screenshot["folder_id"] = None
    _write_json(SCREENSHOTS_FILE, screenshots)
    
    return True

def search_screenshots(
    user_id: str,
    query: str = None,
    tags: List[str] = None,
    start_date: datetime = None,
    end_date: datetime = None,
    folder_id: str = None,
    skip: int = 0,
    limit: int = 10
) -> Tuple[List[dict], int]:
    """
    Search screenshots with multiple criteria
    Args:
        user_id: User ID
        query: Search query for description
        tags: List of tags to search
        start_date: Start date for date range
        end_date: End date for date range
        folder_id: Folder ID to filter by
        skip: Number of results to skip
        limit: Maximum number of results to return
    Returns:
        Tuple of (screenshots, total_count)
    """
    try:
        # Base query
        base_query = {"user_id": user_id}
        
        # Add description search
        if query:
            base_query["$or"] = [
                {"description": {"$regex": query, "$options": "i"}},
                {"filename": {"$regex": query, "$options": "i"}}
            ]
        
        # Add tags search
        if tags:
            base_query["tags"] = {"$all": tags}
        
        # Add date range
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            base_query["created_at"] = date_query
        
        # Add folder filter
        if folder_id:
            base_query["folder_id"] = folder_id
        
        # Get total count
        total = screenshots_collection.count_documents(base_query)
        
        # Get paginated results
        results = list(screenshots_collection.find(
            base_query,
            {"_id": 0}  # Exclude MongoDB _id field
        ).skip(skip).limit(limit))
        
        return results, total
    except Exception as e:
        print(f"Error searching screenshots: {e}")
        return [], 0

def get_search_history(user_id: str, limit: int = 10) -> List[dict]:
    """
    Get user's search history
    Args:
        user_id: User ID
        limit: Maximum number of history items to return
    Returns:
        List of search history items
    """
    try:
        return list(search_history_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit))
    except Exception as e:
        print(f"Error getting search history: {e}")
        return []

def save_search_history(user_id: str, search_params: dict):
    """
    Save a search to history
    Args:
        user_id: User ID
        search_params: Search parameters used
    """
    try:
        search_history_collection.insert_one({
            "user_id": user_id,
            "search_params": search_params,
            "created_at": datetime.utcnow()
        })
    except Exception as e:
        print(f"Error saving search history: {e}")

def get_popular_tags(user_id: str, limit: int = 10) -> List[dict]:
    """
    Get most used tags
    Args:
        user_id: User ID
        limit: Maximum number of tags to return
    Returns:
        List of tags with counts
    """
    try:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        return list(screenshots_collection.aggregate(pipeline))
    except Exception as e:
        print(f"Error getting popular tags: {e}")
        return []

def update_user(username: str, update_data: dict) -> bool:
    """Update user information"""
    try:
        users_collection.update_one(
            {"username": username},
            {"$set": update_data}
        )
        return True
    except Exception as e:
        print(f"Error updating user: {e}")
        return False

def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    try:
        return users_collection.find_one({"email": email})
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

def create_password_reset_token(username: str, token: str, expiry: datetime) -> bool:
    """Create password reset token"""
    try:
        password_reset_tokens_collection.insert_one({
            "username": username,
            "token": token,
            "expiry": expiry,
            "used": False
        })
        return True
    except Exception as e:
        print(f"Error creating password reset token: {e}")
        return False

def verify_password_reset_token(token: str) -> Optional[dict]:
    """Verify password reset token"""
    try:
        reset_token = password_reset_tokens_collection.find_one({
            "token": token,
            "used": False,
            "expiry": {"$gt": datetime.utcnow()}
        })
        
        if reset_token:
            # Mark token as used
            password_reset_tokens_collection.update_one(
                {"_id": reset_token["_id"]},
                {"$set": {"used": True}}
            )
            return get_user(username=reset_token["username"])
        return None
    except Exception as e:
        print(f"Error verifying password reset token: {e}")
        return None

def get_categories():
    """Get all available categories"""
    return [
        "Work Documents",
        "Code Snippets",
        "Error Messages",
        "Chat Records",
        "Web Screenshots",
        "System Settings",
        "Others"
    ]

def update_screenshot_category(screenshot_id: str, user_id: str, category: str) -> bool:
    """Update screenshot category"""
    screenshots = _read_json(SCREENSHOTS_FILE)
    for i, screenshot in enumerate(screenshots):
        if screenshot["id"] == screenshot_id and screenshot["user_id"] == user_id:
            screenshots[i]["category"] = category
            _write_json(SCREENSHOTS_FILE, screenshots)
            return True
    return False

def get_screenshots_by_category(
    user_id: str,
    category: str,
    skip: int = 0,
    limit: int = 10
) -> Tuple[List[dict], int]:
    """Get screenshots by category"""
    screenshots = _read_json(SCREENSHOTS_FILE)
    filtered = [s for s in screenshots if s["user_id"] == user_id and s.get("category") == category]
    total = len(filtered)
    return filtered[skip:skip + limit], total

def get_category_stats(user_id: str) -> dict:
    """Get category statistics for user"""
    screenshots = _read_json(SCREENSHOTS_FILE)
    user_screenshots = [s for s in screenshots if s["user_id"] == user_id]
    
    stats = {}
    for category in get_categories():
        stats[category] = len([s for s in user_screenshots if s.get("category") == category])
    
    # Add uncategorized count
    stats["Uncategorized"] = len([s for s in user_screenshots if not s.get("category")])
    
    return stats
