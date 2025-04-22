from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status, Query, Response, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.sessions import SessionMiddleware
from app.photos import save_upload_file, delete_upload_file
from app.vision import get_image_labels
from app.db.mongo_utils import (
    insert_screenshot,
    get_user,
    create_user,
    get_screenshots,
    get_screenshot_by_id,
    update_screenshot,
    delete_screenshot,
    get_screenshot_count,
    create_folder,
    get_user_folders,
    delete_folder,
    search_screenshots,
    get_search_history,
    save_search_history,
    get_popular_tags,
    update_user,
    get_categories,
    update_screenshot_category,
    get_screenshots_by_category,
    get_category_stats
)
from app.core.security import verify_password, get_password_hash, create_access_token, verify_token
from app.models.user import UserCreate, User
from app.models.folder import FolderCreate, Folder
from typing import List, Optional
from datetime import datetime
import os
import webbrowser
import threading
import time
import json

# Create necessary directories
UPLOAD_DIR = "uploaded_screenshots"
DB_DIR = "local_db"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

# Initialize database files
DB_FILES = {
    "users.json": [],
    "screenshots.json": [],
    "folders.json": [],
    "search_history.json": []
}

for filename, initial_data in DB_FILES.items():
    filepath = os.path.join(DB_DIR, filename)
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            json.dump(initial_data, f)

# Initialize FastAPI application
app = FastAPI(
    title="Smart Screenshot Sorter API",
    description="API for managing and categorizing screenshots",
    version="1.0.0"
)

# Add CORS and Session middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here" 
)

# Function to open browser
def open_browser():
    time.sleep(2)  # Wait a bit longer for server to start
    try:
        webbrowser.open("http://localhost:8000")  # Open the main page instead of docs
    except Exception as e:
        print(f"Could not open browser: {e}")

# Start browser in a separate thread
if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()

@app.get("/")
async def root():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Screenshot Manager</title>
        <style>
            /* Reset default styles */
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
                color: #333;
            }
            
            /* Container for content */
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            
            /* Header section */
            .header {
                text-align: center;
                padding: 40px 0;
                background: #fff;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .header h1 {
                color: #2c3e50;
                margin: 0;
                font-size: 2.5em;
            }
            .header p {
                color: #7f8c8d;
                margin: 10px 0 0;
            }
            
            /* Card styles */
            .card {
                background: #fff;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .card h2 {
                color: #2c3e50;
                margin-top: 0;
            }
            
            /* Button styles */
            .button {
                display: inline-block;
                padding: 10px 20px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin: 10px 0;
                transition: background 0.3s;
            }
            .button:hover {
                background: #2980b9;
            }
            
            /* Features grid */
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .feature {
                background: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .feature h3 {
                color: #2c3e50;
                margin-top: 0;
            }
            .feature p {
                color: #7f8c8d;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <h1>Smart Screenshot Manager</h1>
                <p>Easily manage, categorize and search your screenshots</p>
            </div>
        </div>
        
        <div class="container">
            <div class="card">
                <h2>Get Started</h2>
                <p>Register now and start managing your screenshots!</p>
                <a href="/register" class="button">Register</a>
                <a href="/login" class="button">Login</a>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>Smart Categorization</h3>
                    <p>Automatically recognize and categorize screenshot content</p>
                </div>
                <div class="feature">
                    <h3>Folder Management</h3>
                    <p>Create custom folders to organize your screenshots</p>
                </div>
                <div class="feature">
                    <h3>Quick Search</h3>
                    <p>Find screenshots quickly by description or tags</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

async def get_current_user(request: Request):
    username = request.session.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login first"
        )
    user = get_user(username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@app.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    db_user = get_user(username=username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(password)
    new_user = {
        "username": username,
        "hashed_password": hashed_password,
        "is_active": True
    }
    user = create_user(new_user)
    
    # Auto login after registration
    request.session["username"] = username
    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    user = get_user(username=username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    request.session["username"] = username
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(current_user: User = Depends(get_current_user)):
    # Get user's folders and screenshots
    folders = get_user_folders(current_user.username)
    screenshots = get_screenshots(current_user.username, limit=50)
    categories = get_categories()
    stats = get_category_stats(current_user.username)
    
    # Generate categories HTML
    categories_html = """
        <div class="categories">
            <h3>Categories</h3>
            <div class="category-list">
                """ + "".join([
                    f"""
                    <div class="category-item" onclick="filterByCategory('{category}')">
                        <span>{category}</span>
                        <span class="count">{stats.get(category, 0)}</span>
                    </div>
                    """ for category in categories
                ]) + """
                <div class="category-item" onclick="filterByCategory('')">
                    <span>Uncategorized</span>
                    <span class="count">{stats.get('Uncategorized', 0)}</span>
                </div>
            </div>
        </div>
    """
    
    # Generate screenshots HTML with category selection
    screenshots_html = "".join([
        f"""
        <div class="screenshot-card" draggable="true" ondragstart="drag(event, '{s['id']}')">
            <img src="/screenshots/image/{s['id']}" alt="Screenshot" class="thumbnail">
            <div class="screenshot-info">
                <p>{s['description'] or 'No description'}</p>
                <p>Category: {s.get('category', 'Uncategorized')}</p>
                <p>Uploaded: {s['created_at']}</p>
            </div>
            <div class="screenshot-actions">
                <select class="category-select" onchange="updateCategory('{s['id']}', this.value)">
                    <option value="">Select Category</option>
                    {' '.join(f'<option value="{cat}" {"selected" if s.get("category") == cat else ""}>{cat}</option>' for cat in categories)}
                </select>
                <button class="button edit" onclick="editDescription('{s['id']}')">Edit</button>
                <button class="button delete" onclick="deleteScreenshot('{s['id']}')">Delete</button>
            </div>
        </div>
        """ for s in screenshots
    ])

    return f"""
    <html>
        <head>
            <title>Dashboard - Smart Screenshot Manager</title>
            <style>
                /* Reset default styles */
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    background: #f5f5f5;
                    color: #333;
                }}
                
                /* Layout */
                .dashboard {{
                    display: grid;
                    grid-template-columns: 250px 1fr;
                    gap: 20px;
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                
                /* Folder list styles */
                .folder-list {{
                    background: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .folder-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }}
                .folder-items {{
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }}
                .folder-item {{
                    padding: 10px;
                    background: #f5f5f5;
                    border-radius: 4px;
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .folder-item:hover {{
                    background: #e9e9e9;
                }}
                .delete-folder {{
                    background: none;
                    border: none;
                    color: #ff4444;
                    cursor: pointer;
                    font-size: 18px;
                }}
                
                /* Main content area */
                .main-content {{
                    background: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                
                /* Upload area */
                .upload-area {{
                    border: 2px dashed #3498db;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    margin-bottom: 20px;
                    cursor: pointer;
                }}
                .upload-area:hover {{
                    background: #f0f8ff;
                }}
                .upload-area input {{
                    display: none;
                }}
                
                /* Screenshot grid */
                .screenshot-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    gap: 20px;
                }}
                .screenshot-card {{
                    background: #fff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .thumbnail {{
                    width: 100%;
                    height: 150px;
                    object-fit: cover;
                }}
                .screenshot-info {{
                    padding: 10px;
                }}
                .screenshot-actions {{
                    display: flex;
                    gap: 10px;
                    padding: 10px;
                }}
                
                /* Button styles */
                .button {{
                    padding: 8px 16px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                }}
                .button.primary {{
                    background: #3498db;
                    color: white;
                }}
                .button.edit {{
                    background: #2ecc71;
                    color: white;
                }}
                .button.delete {{
                    background: #e74c3c;
                    color: white;
                }}
                
                /* Category styles */
                .categories {{
                    background: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                .category-list {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin-top: 10px;
                }}
                .category-item {{
                    padding: 8px 16px;
                    background: #f5f5f5;
                    border-radius: 20px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                .category-item:hover {{
                    background: #e9e9e9;
                }}
                .category-item .count {{
                    background: #3498db;
                    color: white;
                    padding: 2px 8px;
                    border-radius: 10px;
                    font-size: 12px;
                }}
                .category-select {{
                    padding: 6px;
                    border-radius: 4px;
                    border: 1px solid #ddd;
                    margin-right: 10px;
                }}
            </style>
            <script>
                // Handle file selection
                function handleFileSelect(event) {{
                    const files = event.target.files;
                    const formData = new FormData();
                    
                    for (let i = 0; i < files.length; i++) {{
                        formData.append('files', files[i]);
                    }}
                    
                    // Add description if provided
                    const description = document.getElementById('description').value;
                    if (description) {{
                        formData.append('description', description);
                    }}
                    
                    // Add folder if selected
                    const folderSelect = document.getElementById('folder-select');
                    if (folderSelect.value) {{
                        formData.append('folder_id', folderSelect.value);
                    }}
                    
                    // Upload files
                    fetch('/screenshots/batch-upload', {{
                        method: 'POST',
                        body: formData
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.results) {{
                            alert('Uploaded ' + data.results.length + ' files successfully!');
                            location.reload();
                        }} else {{
                            alert('Upload failed: ' + data.detail);
                        }}
                    }})
                    .catch(error => {{
                        alert('Upload failed: ' + error);
                    }});
                }}
                
                // Create new folder
                function createFolder() {{
                    const name = prompt('Enter folder name:');
                    if (name) {{
                        fetch('/folders/', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ name }})
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            location.reload();
                        }});
                    }}
                }}
                
                // Delete folder
                function deleteFolder(id) {{
                    if (confirm('Are you sure you want to delete this folder?')) {{
                        fetch(`/folders/${{id}}`, {{
                            method: 'DELETE'
                        }})
                        .then(response => {{
                            if (response.ok) {{
                                location.reload();
                            }}
                        }});
                    }}
                }}
                
                // Select folder
                function selectFolder(id) {{
                    // Update UI
                    document.querySelectorAll('.folder-item').forEach(item => {{
                        item.style.background = '#f5f5f5';
                    }});
                    event.currentTarget.style.background = '#e9e9e9';
                    
                    // TODO: Filter screenshots by folder
                }}
                
                // Edit description
                function editDescription(id) {{
                    const newDescription = prompt('Enter new description:');
                    if (newDescription !== null) {{
                        fetch(`/screenshots/${{id}}`, {{
                            method: 'PUT',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ description: newDescription }})
                        }})
                        .then(response => {{
                            if (response.ok) {{
                                location.reload();
                            }}
                        }});
                    }}
                }}
                
                // Delete screenshot
                function deleteScreenshot(id) {{
                    if (confirm('Are you sure you want to delete this screenshot?')) {{
                        fetch(`/screenshots/${{id}}`, {{
                            method: 'DELETE'
                        }})
                        .then(response => {{
                            if (response.ok) {{
                                location.reload();
                            }}
                        }});
                    }}
                }}
                
                // Drag and drop
                function drag(event, id) {{
                    event.dataTransfer.setData('text/plain', id);
                }}
                
                function allowDrop(event) {{
                    event.preventDefault();
                }}
                
                function drop(event, folderId) {{
                    event.preventDefault();
                    const screenshotId = event.dataTransfer.getData('text/plain');
                    moveToFolder(screenshotId, folderId);
                }}
                
                function moveToFolder(screenshotId, folderId) {{
                    fetch(`/screenshots/${{screenshotId}}`, {{
                        method: 'PUT',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ folder_id: folderId }})
                    }})
                    .then(response => {{
                        if (response.ok) {{
                            location.reload();
                        }}
                    }});
                }}
                
                // Update screenshot category
                function updateCategory(id, category) {{
                    fetch(`/screenshots/${{id}}/category`, {{
                        method: 'PUT',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ category }})
                    }})
                    .then(response => {{
                        if (response.ok) {{
                            location.reload();
                        }}
                    }});
                }}
                
                // Filter screenshots by category
                function filterByCategory(category) {{
                    window.location.href = `/screenshots/category/${{category}}`;
                }}
            </script>
        </head>
        <body>
            <div class="dashboard">
                {categories_html}
                
                <div class="main-content">
                    <h2>Welcome, {current_user.username}!</h2>
                    
                    <div class="upload-area" onclick="document.getElementById('file-input').click()">
                        <input type="file" id="file-input" multiple accept="image/*" onchange="handleFileSelect(event)">
                        <p>Click or drag files here to upload</p>
                        <p>You can select multiple files</p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <input type="text" id="description" placeholder="Description (optional)" style="width: 100%; padding: 10px; margin-bottom: 10px;">
                        <select id="category-select" style="width: 100%; padding: 10px; margin-bottom: 10px;">
                            <option value="">Select Category (optional)</option>
                            {' '.join(f'<option value="{cat}">{cat}</option>' for cat in categories)}
                        </select>
                    </div>
                    
                    <div class="screenshot-grid">
                        {screenshots_html}
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/screenshots/image/{screenshot_id}")
async def get_screenshot_image(
    screenshot_id: str,
    current_user: User = Depends(get_current_user)
):
    screenshot = get_screenshot_by_id(screenshot_id, current_user.username)
    if not screenshot:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return FileResponse(screenshot["file_path"])

@app.get("/screenshots/")
async def list_screenshots(
    current_user: User = Depends(get_current_user),
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        screenshots = get_screenshots(
            user_id=current_user.username,
            category=category,
            search_term=search,
            skip=skip,
            limit=limit
        )
        total = get_screenshot_count(current_user.username, category)
        
        return {
            "total": total,
            "screenshots": screenshots
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/screenshots/{screenshot_id}")
async def get_screenshot(
    screenshot_id: str,
    current_user: User = Depends(get_current_user)
):
    screenshot = get_screenshot_by_id(screenshot_id, current_user.username)
    if not screenshot:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return screenshot

@app.put("/screenshots/{screenshot_id}")
async def update_screenshot_info(
    screenshot_id: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    update_data = {}
    if description is not None:
        update_data["description"] = description
    if category is not None:
        update_data["category"] = category
        
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
        
    success = update_screenshot(screenshot_id, current_user.username, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Screenshot not found")
        
    return {"message": "Screenshot updated successfully"}

@app.delete("/screenshots/{screenshot_id}")
async def delete_screenshot_endpoint(
    screenshot_id: str,
    current_user: User = Depends(get_current_user)
):
    # Get screenshot info first
    screenshot = get_screenshot_by_id(screenshot_id, current_user.username)
    if not screenshot:
        raise HTTPException(status_code=404, detail="Screenshot not found")
        
    # Delete file from storage
    try:
        delete_upload_file(screenshot["file_path"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
        
    # Delete from database
    success = delete_screenshot(screenshot_id, current_user.username)
    if not success:
        raise HTTPException(status_code=500, detail="Error deleting screenshot from database")
        
    return {"message": "Screenshot deleted successfully"}

@app.post("/folders/", response_model=Folder)
async def create_folder(
    folder: FolderCreate,
    current_user: User = Depends(get_current_user)
):
    folder_data = folder.dict()
    folder_data["user_id"] = current_user.username
    folder_id = create_folder(folder_data)
    return {**folder_data, "id": folder_id}

@app.get("/folders/", response_model=List[Folder])
async def list_folders(
    parent_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    return get_user_folders(current_user.username, parent_id)

@app.delete("/folders/{folder_id}")
async def delete_folder_endpoint(
    folder_id: str,
    current_user: User = Depends(get_current_user)
):
    success = delete_folder(folder_id, current_user.username)
    if not success:
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"message": "Folder deleted successfully"}

@app.post("/screenshots/batch-upload")
async def batch_upload_screenshots(
    files: List[UploadFile] = File(...),
    folder_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    results = []
    for file in files:
        try:
            if not file.content_type.startswith('image/'):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "File must be an image"
                })
                continue
                
            path = save_upload_file(file)
            labels = get_image_labels(path)

            metadata = {
                "filename": file.filename,
                "file_path": path,
                "vision_tags": labels,
                "description": description,
                "folder_id": folder_id,
                "user_id": current_user.username,
                "ml_prediction": None,
                "feedback_corrected": False
            }

            inserted_id = insert_screenshot(metadata)
            results.append({
                "filename": file.filename,
                "success": True,
                "id": inserted_id,
                "labels": labels
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return {"results": results}

@app.get("/screenshots/search")
async def search_screenshots_endpoint(
    query: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    folder_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    # Search screenshots
    results, total = search_screenshots(
        user_id=current_user.username,
        query=query,
        tags=tags,
        start_date=start_date,
        end_date=end_date,
        folder_id=folder_id,
        skip=skip,
        limit=limit
    )
    
    # Save search to history
    if query or tags:
        save_search_history(current_user.username, {
            "query": query,
            "tags": tags,
            "start_date": start_date,
            "end_date": end_date,
            "folder_id": folder_id
        })
    
    return {
        "total": total,
        "results": results
    }

@app.get("/screenshots/search/history")
async def get_search_history_endpoint(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    history = get_search_history(current_user.username, limit)
    return {"history": history}

@app.get("/screenshots/tags/popular")
async def get_popular_tags_endpoint(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    tags = get_popular_tags(current_user.username, limit)
    return {"tags": tags}

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - Smart Screenshot Manager</title>
        <style>
            /* Reset default styles */
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
                color: #333;
            }
            
            /* Container for content */
            .container {
                max-width: 400px;
                margin: 50px auto;
                padding: 20px;
            }
            
            /* Form card */
            .card {
                background: #fff;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            /* Form elements */
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
                color: #2c3e50;
            }
            .form-group input {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }
            
            /* Button styles */
            .button {
                display: block;
                width: 100%;
                padding: 12px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.3s;
            }
            .button:hover {
                background: #2980b9;
            }
            
            /* Back link */
            .back-link {
                display: block;
                text-align: center;
                margin-top: 20px;
                color: #3498db;
                text-decoration: none;
            }
            .back-link:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h2 style="text-align: center; margin-bottom: 30px;">Create Account</h2>
                <form action="/register" method="post">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="button">Register</button>
                </form>
                <a href="/" class="back-link">Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - Smart Screenshot Manager</title>
        <style>
            /* Reset default styles */
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
                color: #333;
            }
            
            /* Container for content */
            .container {
                max-width: 400px;
                margin: 50px auto;
                padding: 20px;
            }
            
            /* Form card */
            .card {
                background: #fff;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            /* Form elements */
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
                color: #2c3e50;
            }
            .form-group input {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }
            
            /* Button styles */
            .button {
                display: block;
                width: 100%;
                padding: 12px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.3s;
            }
            .button:hover {
                background: #2980b9;
            }
            
            /* Links */
            .links {
                text-align: center;
                margin-top: 20px;
            }
            .links a {
                color: #3498db;
                text-decoration: none;
                margin: 0 10px;
            }
            .links a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h2 style="text-align: center; margin-bottom: 30px;">Login</h2>
                <form action="/login" method="post">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="button">Login</button>
                </form>
                <div class="links">
                    <a href="/">Back to Home</a>
                    <a href="/register">Create Account</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/categories")
async def get_available_categories():
    """Get list of all available categories"""
    return get_categories()

@app.put("/screenshots/{screenshot_id}/category")
async def update_category(
    screenshot_id: str,
    category: str,
    current_user: User = Depends(get_current_user)
):
    """
    Update screenshot category
    Args:
        screenshot_id: ID of the screenshot
        category: New category name
        current_user: Current authenticated user
    """
    success = update_screenshot_category(screenshot_id, current_user.username, category)
    if not success:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return {"message": "Category updated successfully"}

@app.get("/screenshots/category/{category}")
async def get_category_screenshots(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """
    Get screenshots by category
    Args:
        category: Category to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
    """
    screenshots, total = get_screenshots_by_category(
        current_user.username,
        category,
        skip,
        limit
    )
    return {
        "total": total,
        "screenshots": screenshots
    }

@app.get("/categories/stats")
async def get_categories_stats(current_user: User = Depends(get_current_user)):
    """
    Get statistics for each category
    Args:
        current_user: Current authenticated user
    """
    return get_category_stats(current_user.username)
