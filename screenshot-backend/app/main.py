from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from starlette.middleware.sessions import SessionMiddleware
import os
import shutil
import uuid
from typing import Dict, List, Optional
import requests
import json
import base64
from google.cloud import vision
from google.oauth2 import service_account
import zipfile
from datetime import datetime
from collections import Counter
import io

UPLOAD_DIR = "uploaded_screenshots"
os.makedirs(UPLOAD_DIR, exist_ok=True)

CATEGORIES = ["Work", "Personal", "Others"]
GOOGLE_VISION_API_KEY = "AIzaSyBRWvxcv7-Mxv-y7veUOf93qsI0YalmBYo"
VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"

# Service account credentials as dict
SERVICE_ACCOUNT_INFO = {
  "type": "service_account",
  "project_id": "smart-screenshot-manager",
  "private_key_id": "7e18414457cc8559e27d8c7ddcec701f7435624a",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCwZZ4P02uLNbGC\nYIvr4JwRlcBUCThRVEGPwrz3fzHnoJyeDw+KM2CKLMMhp8VX6nS+IT07ZSIzt25s\nlE7LjLfKVIpLaO05zaPwH1P9Z8K/hNzdDnKL9Syc58pZ8f0mqa3k6bCvi0JpZrsh\nK7CWWzgVH4H/tdr4sdUELq0IKYzPH/iWaq5G4oceceZZLnuiK3BdCvY4fiQm6J4F\ndeGyKifOcpOMvpgfzC8etIZzsvteDljg5v78e4shq0EXTaumZtnO5Q1Li0yyO339\nBaj7u/TF9mTihkZ1gOOFrI07pF9UyTvNttPIQ6ZjWArkOcWPkwbeV/0E0/anwUei\ndOFuU2fXAgMBAAECggEAD3+45fkUmkm1zBfW6NB2cLvGB1w8B4wDVVyt+oJsNxw5\n8VAEydwpH7A+gPGFzxYO+zmzxfPlOm1j6sRpMUyu8BHXiOKySAGVOvRLDpk/AlGW\nj7xvkh6RCe76gkaskJNuGmPyHf/QGQS+wnOyngjBImdUpnbVw5jpzOabq3uYdLEG\nxPi7s2vmzj8bYsnK6gfSiswJZ3AdC9IX6dov8/v6GKw0U0gcywSj4TVVHt8jtOjD\nwqJtBRW53KM4vqYCJ35KZjrhj4w7GoLKnyCKy6kXcDgqRYUyndZVU246W6QpJyo4\nEzZ0fPHKRI+WWxv0ZrCrxa3pFISWvphB5XMkC+rg8QKBgQDXI2HzfUuuzqxuU6OV\ns3k2sn6w8ybhrt1bCCsTGY5/PkKMbBcl6TDWziqU4doCedDBuXoSQ+FBaCHlaP18\nAGC/+76Fvp4JHCWl6t4PnwqNt5y/2frjNbk41Vy1Xxwq+T/F1L+omB8DFoCmFoX/\nOwAwIUldrKX/HOTjcNkNXRTBnwKBgQDR5obTO2rpOnruJj2KdkIbrKf5Lu0ajJeF\nf/4CHVDzpwKudUQ6mzHHOj3Rbs26fHTOaVjvLFYbj9jBt1laZOdbI5sTgz6P8h3a\n8w6SswTu9onnSeuaH2rRXLy2t4kLJV8VFLK3vorV90R7Gt3HbY4uDUl603HbPp3V\nO2rURbFeyQKBgCK+fBsuqQJaLk7DAzAyA+lpejxpiGX6L5V8BDjZb8Hs9CJpcnOU\n7WZDdW0F7Idp1OT0Z1p7y+0cPB0oj4dvKDDZHzPKTQt7mDjrbWFodfPdK1twgKwh\nCQC8tHQ2H/5wsnPon+tCZf/BqpUoHgvSI32iYo7WSxigOfbhSqx109xRAoGASx1h\nMGR6DP7FkUYUDeHmJHs0HWNirHaVnsu//ce5+YfR2NbUVNjHBpHcH3+0lcEGF/vx\nPJ40Lmba3fAcRNIJTT8/tsrn76Fod7s1guAXquCFV0TH0H7fvg6e5hBmNZvpG+Ut\nU74Xdxym4BssNLsK/4X3vsG+ZARTfURnJZHPOKkCgYB8tbJSJIqKqieUkocK96lP\n5G1KWaOVZDAZiyIJ0CtWzusRojbzCFe7Y/6DDbTNVvZuwUlAMPgvQ5AciTxWDqG8\nbS5MMFolXvftOWR6vFMgurnZRVl7/6eGzUof9mL7ous71k8n2kAwRt+v0HlHQudZ\n5d/P0IM96f242Rrcfi1q5w==\n-----END PRIVATE KEY-----\n",
  "client_email": "vision-sa@smart-screenshot-manager.iam.gserviceaccount.com",
  "client_id": "101403860215420491771",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/vision-sa%40smart-screenshot-manager.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Initialize Google Vision client with service account
credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO)
vision_client = vision.ImageAnnotatorClient(credentials=credentials)

app = FastAPI(title="Smart Screenshot Sorter")
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-here")

users: Dict[str, Dict] = {}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = request.session.get("user")
    if user:
        # Logged in
        links = """
            <a href='/upload'>Upload Screenshot</a>
            <a href='/view'>View Screenshots</a>
            <a href='/search'>Search Screenshots</a>
            <a href='/export'>Export Screenshots</a>
            <a href='/delete'>Delete Screenshots</a>
            <a href='/stats'>View Statistics</a>
            <a href='/logout'>Logout</a>
        """
    else:
        # Not logged in
        links = """
            <a href='/register'>Register</a>
            <a href='/login'>Login</a>
        """
    return f"""
    <html>
    <head>
        <title>Smart Screenshot Manager</title>
        <style>
            body {{
                background: linear-gradient(135deg, #232526 0%, #414345 100%);
                min-height: 100vh;
                margin: 0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .center-box {{
                background: rgba(30, 32, 34, 0.97);
                border-radius: 18px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                padding: 48px 40px 40px 40px;
                min-width: 350px;
                display: flex;
                flex-direction: column;
                align-items: center;
                border: 1px solid rgba(255,255,255,0.08);
            }}
            .main-title {{
                color: #00eaff;
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 36px;
                letter-spacing: 2px;
                text-shadow: 0 0 12px #00eaff44;
                text-align: center;
            }}
            .main-links {{
                display: flex;
                flex-direction: column;
                gap: 24px;
                width: 100%;
                align-items: center;
            }}
            .main-links a {{
                display: block;
                width: 220px;
                padding: 18px 0;
                font-size: 1.4rem;
                font-weight: bold;
                color: #fff;
                background: linear-gradient(90deg, #00eaff 0%, #005bea 100%);
                border-radius: 10px;
                text-align: center;
                text-decoration: none;
                margin: 0 auto;
                box-shadow: 0 2px 8px #00eaff33;
                letter-spacing: 1px;
                transition: background 0.2s, box-shadow 0.2s, color 0.2s;
            }}
            .main-links a:hover {{
                background: linear-gradient(90deg, #005bea 0%, #00eaff 100%);
                color: #00eaff;
                box-shadow: 0 4px 16px #00eaff55;
            }}
        </style>
    </head>
    <body>
        <div class="center-box">
            <div class="main-title">Welcome to<br>Smart Screenshot Manager!</div>
            <div class="main-links">
                {links}
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    return """
    <html>
    <head>
        <title>Register - Smart Screenshot Manager</title>
        <style>
            body {
                background: linear-gradient(135deg, #232526 0%, #414345 100%);
                min-height: 100vh;
                margin: 0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .register-container {
                background: rgba(30, 32, 34, 0.97);
                border-radius: 18px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                padding: 48px 40px 40px 40px;
                min-width: 350px;
                display: flex;
                flex-direction: column;
                align-items: center;
                border: 1px solid rgba(255,255,255,0.08);
            }
            .register-title {
                color: #00eaff;
                font-size: 2.2rem;
                font-weight: bold;
                margin-bottom: 32px;
                letter-spacing: 2px;
                text-shadow: 0 0 10px #00eaff44;
                text-align: center;
            }
            .register-form {
                width: 100%;
                display: flex;
                flex-direction: column;
                gap: 22px;
            }
            .register-form input {
                padding: 14px;
                border-radius: 8px;
                border: none;
                background: #232526;
                color: #fff;
                font-size: 1.1rem;
                outline: none;
                box-shadow: 0 2px 8px #00eaff11;
                transition: box-shadow 0.2s;
            }
            .register-form input:focus {
                box-shadow: 0 0 8px #00eaff88;
            }
            .register-form button {
                padding: 14px;
                border-radius: 8px;
                border: none;
                background: linear-gradient(90deg, #00eaff 0%, #005bea 100%);
                color: #fff;
                font-size: 1.2rem;
                font-weight: bold;
                cursor: pointer;
                letter-spacing: 1px;
                box-shadow: 0 2px 8px #00eaff33;
                transition: background 0.2s, box-shadow 0.2s;
            }
            .register-form button:hover {
                background: linear-gradient(90deg, #005bea 0%, #00eaff 100%);
                box-shadow: 0 4px 16px #00eaff55;
            }
            .links {
                margin-top: 22px;
                text-align: center;
            }
            .links a {
                color: #00eaff;
                text-decoration: none;
                margin: 0 10px;
                font-size: 1.1rem;
                transition: color 0.2s;
            }
            .links a:hover {
                color: #fff;
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="register-container">
            <div class="register-title">Register</div>
            <form class="register-form" action="/register" method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Register</button>
            </form>
            <div class="links">
                <a href="/">Back to Home</a>
                <a href="/login">Login</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in users:
        return HTMLResponse("Username already exists.", status_code=400)
    users[username] = {"password": password}
    request.session["user"] = username
    return RedirectResponse("/upload", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return """
    <html>
    <head>
        <title>Login - Smart Screenshot Manager</title>
        <style>
            body {
                background: linear-gradient(135deg, #232526 0%, #414345 100%);
                min-height: 100vh;
                margin: 0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .login-container {
                background: rgba(30, 32, 34, 0.95);
                border-radius: 16px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                padding: 40px 32px 32px 32px;
                width: 350px;
                display: flex;
                flex-direction: column;
                align-items: center;
                border: 1px solid rgba(255,255,255,0.08);
            }
            .login-title {
                color: #00eaff;
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 24px;
                letter-spacing: 2px;
                text-shadow: 0 0 8px #00eaff44;
            }
            .login-form {
                width: 100%;
                display: flex;
                flex-direction: column;
                gap: 18px;
            }
            .login-form input {
                padding: 12px;
                border-radius: 8px;
                border: none;
                background: #232526;
                color: #fff;
                font-size: 1rem;
                outline: none;
                box-shadow: 0 2px 8px #00eaff11;
                transition: box-shadow 0.2s;
            }
            .login-form input:focus {
                box-shadow: 0 0 8px #00eaff88;
            }
            .login-form button {
                padding: 12px;
                border-radius: 8px;
                border: none;
                background: linear-gradient(90deg, #00eaff 0%, #005bea 100%);
                color: #fff;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                letter-spacing: 1px;
                box-shadow: 0 2px 8px #00eaff33;
                transition: background 0.2s, box-shadow 0.2s;
            }
            .login-form button:hover {
                background: linear-gradient(90deg, #005bea 0%, #00eaff 100%);
                box-shadow: 0 4px 16px #00eaff55;
            }
            .links {
                margin-top: 18px;
                text-align: center;
            }
            .links a {
                color: #00eaff;
                text-decoration: none;
                margin: 0 10px;
                font-size: 1rem;
                transition: color 0.2s;
            }
            .links a:hover {
                color: #fff;
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="login-title">Smart Screenshot Manager</div>
            <form class="login-form" action="/login" method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <div class="links">
                <a href="/">Back to Home</a>
                <a href="/register">Create Account</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or user["password"] != password:
        return HTMLResponse("Incorrect username or password.", status_code=400)
    request.session["user"] = username
    return RedirectResponse("/upload", status_code=303)

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not hasattr(app, "user_categories"):
        app.user_categories = {}
    if user not in app.user_categories:
        app.user_categories[user] = CATEGORIES.copy()
    
    return f"""
    <html>
    <head>
        <title>Upload Screenshot - Smart Screenshot Manager</title>
        <style>
            body {{
                background: linear-gradient(135deg, #232526 0%, #414345 100%);
                min-height: 100vh;
                margin: 0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .upload-container {{
                background: rgba(30, 32, 34, 0.97);
                border-radius: 18px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                padding: 48px 40px 40px 40px;
                min-width: 350px;
                display: flex;
                flex-direction: column;
                align-items: center;
                border: 1px solid rgba(255,255,255,0.08);
            }}
            .upload-title {{
                color: #00eaff;
                font-size: 2.2rem;
                font-weight: bold;
                margin-bottom: 32px;
                letter-spacing: 2px;
                text-shadow: 0 0 10px #00eaff44;
                text-align: center;
            }}
            .upload-form {{
                width: 100%;
                display: flex;
                flex-direction: column;
                gap: 22px;
            }}
            .upload-form input[type='file'] {{
                padding: 14px;
                border-radius: 8px;
                background: #232526;
                color: #fff;
                font-size: 1.1rem;
                outline: none;
                box-shadow: 0 2px 8px #00eaff11;
                transition: box-shadow 0.2s;
            }}
            .upload-form select {{
                padding: 14px;
                border-radius: 8px;
                background: #232526;
                color: #fff;
                font-size: 1.1rem;
                outline: none;
                box-shadow: 0 2px 8px #00eaff11;
                transition: box-shadow 0.2s;
            }}
            .upload-form button {{
                padding: 14px;
                border-radius: 8px;
                border: none;
                background: linear-gradient(90deg, #00eaff 0%, #005bea 100%);
                color: #fff;
                font-size: 1.2rem;
                font-weight: bold;
                cursor: pointer;
                letter-spacing: 1px;
                box-shadow: 0 2px 8px #00eaff33;
                transition: background 0.2s, box-shadow 0.2s;
            }}
            .upload-form button:hover {{
                background: linear-gradient(90deg, #005bea 0%, #00eaff 100%);
                box-shadow: 0 4px 16px #00eaff55;
            }}
            .links {{
                margin-top: 22px;
                text-align: center;
            }}
            .links a {{
                color: #00eaff;
                text-decoration: none;
                margin: 0 10px;
                font-size: 1.1rem;
                transition: color 0.2s;
            }}
            .links a:hover {{
                color: #fff;
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="upload-container">
            <div class="upload-title">Upload Screenshot</div>
            <form class="upload-form" action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="files" multiple required><br>
                <select name="category" required>
                    <option value="">Select Category</option>
                    {''.join(f'<option value="{cat}">{cat}</option>' for cat in app.user_categories[user])}
                </select>
                <button type="submit">Upload</button>
            </form>
            <div class="links">
                <a href="/">Back to Home</a>
                <a href="/login">Login</a>
                <a href="/view">View Screenshots</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/upload")
async def upload(request: Request, files: List[UploadFile] = File(...), category: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not isinstance(files, list):
        files = [files]
    if not all(f.content_type.startswith("image/") for f in files):
        return HTMLResponse("Only image files are allowed.", status_code=400)
    
    if not hasattr(app, "screenshots"):
        app.screenshots = {}
    results_html = ""
    for file in files:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        analysis = await analyze_image(file_path)
        app.screenshots[file_id] = {
            "filename": file.filename,
            "category": category,
            "user": user,
            "analysis": analysis
        }
        analysis_html = ""
        if analysis:
            analysis_html += "<h3>Analysis Result:</h3>"
            if analysis.get("text"):
                analysis_html += f"<p><b>Text:</b> {analysis['text']}</p>"
            if analysis.get("labels"):
                analysis_html += f"<p><b>Labels:</b> {', '.join(analysis['labels'])}</p>"
            if analysis.get("web_entities"):
                analysis_html += f"<p><b>Web Entities:</b> {', '.join(analysis['web_entities'])}</p>"
            if analysis.get("error"):
                analysis_html += f"<p style='color:red;'><b>Error:</b> {analysis['error']}</p>"
        results_html += f"""
        <div style='margin-bottom:30px;'>
            <h2>Upload successful!</h2>
            <img src='/image/{file_id}_{file.filename}' width='200'><br>
            {analysis_html}
        </div>
        """
    return HTMLResponse(f"""
    <html>
    <head>
        <title>Upload Success</title>
    </head>
    <body>
        {results_html}
        <a href='/upload'>Upload more</a>
        <a href='/view'>View Screenshots</a>
        <a href='/'>Back to Home</a>
    </body>
    </html>
    """)

@app.get("/image/{filename}")
async def get_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return HTMLResponse("Image not found.", status_code=404)

@app.get("/view", response_class=HTMLResponse)
async def view_screenshots(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not hasattr(app, "screenshots"):
        app.screenshots = {}
    if not hasattr(app, "user_categories"):
        app.user_categories = {}
    if user not in app.user_categories:
        app.user_categories[user] = CATEGORIES.copy()
    
    user_screenshots = {k: v for k, v in app.screenshots.items() if v["user"] == user}
    screenshots_html = ""
    for file_id, info in user_screenshots.items():
        analysis = info.get("analysis", {})
        analysis_html = ""
        if analysis:
            if analysis.get("text"):
                analysis_html += f"<p><b>Text:</b> {analysis['text']}</p>"
            if analysis.get("labels"):
                analysis_html += f"<p><b>Labels:</b> {', '.join(analysis['labels'])}</p>"
            if analysis.get("web_entities"):
                analysis_html += f"<p><b>Web Entities:</b> {', '.join(analysis['web_entities'])}</p>"
            if analysis.get("error"):
                analysis_html += f"<p style='color:red;'><b>Error:</b> {analysis['error']}</p>"
        screenshots_html += f"""
        <div style="margin-bottom: 20px; padding: 10px; background: rgba(30, 32, 34, 0.97); border-radius: 8px; box-shadow: 0 2px 8px #00eaff11;">
            <img src='/image/{file_id}_{info["filename"]}' width='200'><br>
            <p>Category: {info["category"]}</p>
            <form action="/update_category" method="post" style="display: inline;">
                <input type="hidden" name="file_id" value="{file_id}">
                <select name="category" onchange="this.form.submit()">
                    {''.join(f'<option value="{cat}" {"selected" if info["category"] == cat else ""}>{cat}</option>' for cat in app.user_categories[user])}
                </select>
            </form>
            {analysis_html}
        </div>
        """
    
    return f"""
    <html>
    <head>
        <title>View Screenshots - Smart Screenshot Manager</title>
        <style>
            body {{
                background: linear-gradient(135deg, #232526 0%, #414345 100%);
                min-height: 100vh;
                margin: 0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
            }}
            .view-title {{
                color: #00eaff;
                font-size: 2.2rem;
                font-weight: bold;
                margin-bottom: 32px;
                letter-spacing: 2px;
                text-shadow: 0 0 10px #00eaff44;
                text-align: center;
            }}
            .category-manager {{
                background: rgba(30, 32, 34, 0.97);
                border-radius: 18px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                padding: 20px;
                margin-bottom: 30px;
                width: 300px;
                text-align: center;
            }}
            .category-manager h3 {{
                color: #00eaff;
                margin-bottom: 15px;
            }}
            .category-form {{
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
            }}
            .category-form input {{
                padding: 8px;
                border-radius: 8px;
                border: none;
                background: #232526;
                color: #fff;
                flex-grow: 1;
            }}
            .category-form button {{
                padding: 8px 15px;
                border-radius: 8px;
                border: none;
                background: linear-gradient(90deg, #00eaff 0%, #005bea 100%);
                color: #fff;
                cursor: pointer;
            }}
            .current-categories {{
                color: #fff;
                margin-top: 15px;
            }}
            .category-item {{
                display: inline-flex;
                align-items: center;
                background: #232526;
                padding: 5px 10px;
                border-radius: 5px;
                margin: 3px;
            }}
            .category-item span {{
                margin-right: 8px;
            }}
            .delete-btn {{
                background: none;
                border: none;
                color: #ff4444;
                cursor: pointer;
                padding: 0 5px;
                font-size: 1.2rem;
                line-height: 1;
            }}
            .delete-btn:hover {{
                color: #ff0000;
            }}
            .links {{
                margin-top: 22px;
                text-align: center;
            }}
            .links a {{
                color: #00eaff;
                text-decoration: none;
                margin: 0 10px;
                font-size: 1.1rem;
                transition: color 0.2s;
            }}
            .links a:hover {{
                color: #fff;
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="view-title">View Screenshots</div>
        
        <div class="category-manager">
            <h3>Manage Categories</h3>
            <form class="category-form" action="/add_category" method="post">
                <input type="text" name="category" placeholder="New category name" required>
                <button type="submit">Add</button>
            </form>
            <div class="current-categories">
                <p>Current Categories:</p>
                {''.join(f'''
                <div class="category-item">
                    <span>{cat}</span>
                    <form action="/delete_category" method="post" style="display: inline;">
                        <input type="hidden" name="category" value="{cat}">
                        <button type="submit" class="delete-btn" onclick="return confirm('Are you sure you want to delete this category?')">×</button>
                    </form>
                </div>
                ''' for cat in app.user_categories[user])}
            </div>
        </div>

        {screenshots_html}
        <div class="links">
            <a href="/">Back to Home</a>
            <a href="/upload">Upload Screenshot</a>
        </div>
    </body>
    </html>
    """

@app.post("/update_category")
async def update_category(request: Request, file_id: str = Form(...), category: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not hasattr(app, "screenshots") or file_id not in app.screenshots or app.screenshots[file_id]["user"] != user:
        return HTMLResponse("Screenshot not found.", status_code=404)
    app.screenshots[file_id]["category"] = category
    return RedirectResponse("/view", status_code=303)

@app.post("/add_category")
async def add_category(request: Request, category: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not hasattr(app, "user_categories"):
        app.user_categories = {}
    if user not in app.user_categories:
        app.user_categories[user] = CATEGORIES.copy()
    
    if category not in app.user_categories[user]:
        app.user_categories[user].append(category)
    
    return RedirectResponse("/view", status_code=303)

@app.post("/delete_category")
async def delete_category(request: Request, category: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not hasattr(app, "user_categories"):
        app.user_categories = {}
    if user not in app.user_categories:
        app.user_categories[user] = CATEGORIES.copy()
    
    if category in CATEGORIES:
        return HTMLResponse("Cannot delete default categories.", status_code=400)
    
    if category in app.user_categories[user]:
        app.user_categories[user].remove(category)
        
        if hasattr(app, "screenshots"):
            for file_id, info in app.screenshots.items():
                if info["user"] == user and info["category"] == category:
                    app.screenshots[file_id]["category"] = "Others"
    
    return RedirectResponse("/view", status_code=303)

@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    
    return """
    <html>
    <head>
        <title>Search Screenshots - Smart Screenshot Manager</title>
        <style>
            body {
                background: linear-gradient(135deg, #232526 0%, #414345 100%);
                min-height: 100vh;
                margin: 0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
            }
            .search-container {
                background: rgba(30, 32, 34, 0.97);
                border-radius: 18px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                padding: 40px;
                width: 600px;
                margin-bottom: 30px;
            }
            .search-title {
                color: #00eaff;
                font-size: 2.2rem;
                font-weight: bold;
                margin-bottom: 32px;
                letter-spacing: 2px;
                text-shadow: 0 0 10px #00eaff44;
                text-align: center;
            }
            .search-form {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }
            .search-form input {
                flex-grow: 1;
                padding: 12px;
                border-radius: 8px;
                border: none;
                background: #232526;
                color: #fff;
                font-size: 1.1rem;
                outline: none;
                box-shadow: 0 2px 8px #00eaff11;
            }
            .search-form button {
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
                background: linear-gradient(90deg, #00eaff 0%, #005bea 100%);
                color: #fff;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                letter-spacing: 1px;
                box-shadow: 0 2px 8px #00eaff33;
                transition: background 0.2s, box-shadow 0.2s;
            }
            .search-form button:hover {
                background: linear-gradient(90deg, #005bea 0%, #00eaff 100%);
                box-shadow: 0 4px 16px #00eaff55;
            }
            .search-results {
                margin-top: 20px;
            }
            .screenshot-item {
                background: rgba(35, 37, 38, 0.97);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .screenshot-item img {
                width: 150px;
                height: 150px;
                object-fit: cover;
                border-radius: 4px;
            }
            .screenshot-info {
                flex-grow: 1;
            }
            .screenshot-info h3 {
                color: #00eaff;
                margin: 0 0 10px 0;
            }
            .screenshot-info p {
                color: #fff;
                margin: 5px 0;
            }
            .links {
                margin-top: 22px;
                text-align: center;
            }
            .links a {
                color: #00eaff;
                text-decoration: none;
                margin: 0 10px;
                font-size: 1.1rem;
                transition: color 0.2s;
            }
            .links a:hover {
                color: #fff;
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="search-container">
            <div class="search-title">Search Screenshots</div>
            <form class="search-form" action="/search" method="post">
                <input type="text" name="query" placeholder="Enter search terms..." required>
                <button type="submit">Search</button>
            </form>
            <div class="search-results">
                <!-- Search results will be displayed here -->
            </div>
        </div>
        <div class="links">
            <a href="/">Back to Home</a>
            <a href="/view">View All Screenshots</a>
        </div>
    </body>
    </html>
    """

@app.post("/search")
async def search_screenshots(request: Request, query: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    
    if not hasattr(app, "screenshots"):
        app.screenshots = {}
    
    # Search through user's screenshots
    results = []
    for file_id, info in app.screenshots.items():
        if info["user"] != user:
            continue
            
        # Search in text content
        if "analysis" in info and "text" in info["analysis"]:
            if query.lower() in info["analysis"]["text"].lower():
                results.append((file_id, info))
                continue
        
        # Search in labels
        if "analysis" in info and "labels" in info["analysis"]:
            if any(query.lower() in label.lower() for label in info["analysis"]["labels"]):
                results.append((file_id, info))
                continue
        
        # Search in web entities
        if "analysis" in info and "web_entities" in info["analysis"]:
            if any(query.lower() in entity.lower() for entity in info["analysis"]["web_entities"]):
                results.append((file_id, info))
                continue
    
    # Generate HTML for search results
    results_html = ""
    for file_id, info in results:
        results_html += f"""
        <div class="screenshot-item">
            <img src='/image/{file_id}_{info["filename"]}' alt="Screenshot">
            <div class="screenshot-info">
                <h3>{info["filename"]}</h3>
                <p>Category: {info["category"]}</p>
                <p>Text Content: {info["analysis"].get("text", "")[:200]}...</p>
                <p>Labels: {", ".join(info["analysis"].get("labels", [])[:5])}</p>
            </div>
        </div>
        """
    
    return HTMLResponse(f"""
    <html>
    <head>
        <title>Search Results - Smart Screenshot Manager</title>
        <style>
            body {{
                background: linear-gradient(135deg, #232526 0%, #414345 100%);
                min-height: 100vh;
                margin: 0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
            }}
            .search-container {{
                background: rgba(30, 32, 34, 0.97);
                border-radius: 18px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                padding: 40px;
                width: 600px;
                margin-bottom: 30px;
            }}
            .search-title {{
                color: #00eaff;
                font-size: 2.2rem;
                font-weight: bold;
                margin-bottom: 32px;
                letter-spacing: 2px;
                text-shadow: 0 0 10px #00eaff44;
                text-align: center;
            }}
            .search-form {{
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }}
            .search-form input {{
                flex-grow: 1;
                padding: 12px;
                border-radius: 8px;
                border: none;
                background: #232526;
                color: #fff;
                font-size: 1.1rem;
                outline: none;
                box-shadow: 0 2px 8px #00eaff11;
            }}
            .search-form button {{
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
                background: linear-gradient(90deg, #00eaff 0%, #005bea 100%);
                color: #fff;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                letter-spacing: 1px;
                box-shadow: 0 2px 8px #00eaff33;
                transition: background 0.2s, box-shadow 0.2s;
            }}
            .search-form button:hover {{
                background: linear-gradient(90deg, #005bea 0%, #00eaff 100%);
                box-shadow: 0 4px 16px #00eaff55;
            }}
            .search-results {{
                margin-top: 20px;
            }}
            .screenshot-item {{
                background: rgba(35, 37, 38, 0.97);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            .screenshot-item img {{
                width: 150px;
                height: 150px;
                object-fit: cover;
                border-radius: 4px;
            }}
            .screenshot-info {{
                flex-grow: 1;
            }}
            .screenshot-info h3 {{
                color: #00eaff;
                margin: 0 0 10px 0;
            }}
            .screenshot-info p {{
                color: #fff;
                margin: 5px 0;
            }}
            .links {{
                margin-top: 22px;
                text-align: center;
            }}
            .links a {{
                color: #00eaff;
                text-decoration: none;
                margin: 0 10px;
                font-size: 1.1rem;
                transition: color 0.2s;
            }}
            .links a:hover {{
                color: #fff;
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="search-container">
            <div class="search-title">Search Results</div>
            <form class="search-form" action="/search" method="post">
                <input type="text" name="query" value="{query}" required>
                <button type="submit">Search</button>
            </form>
            <div class="search-results">
                {results_html if results_html else "<p style='color: #fff; text-align: center;'>No results found.</p>"}
            </div>
        </div>
        <div class="links">
            <a href="/">Back to Home</a>
            <a href="/view">View All Screenshots</a>
        </div>
    </body>
    </html>
    """)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

async def analyze_image(image_path: str) -> Dict:
    try:
        # Read image file
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        # Text detection
        text_response = vision_client.text_detection(image=image)
        texts = text_response.text_annotations
        # Label detection
        label_response = vision_client.label_detection(image=image)
        labels = label_response.label_annotations
        # Web detection
        web_response = vision_client.web_detection(image=image)
        web_entities = web_response.web_detection.web_entities
        return {
            "text": texts[0].description if texts else "",
            "labels": [label.description for label in labels],
            "web_entities": [entity.description for entity in web_entities if entity.description]
        }
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return {"error": str(e)}

@app.get("/export", response_class=HTMLResponse)
async def export_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    
    return """
    <html>
    <head>
        <title>Export Screenshots - Smart Screenshot Manager</title>
        <style>
            body {
                background: linear-gradient(135deg, #232526 0%, #414345 100%);
                min-height: 100vh;
                margin: 0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
            }
            .export-container {
                background: rgba(30, 32, 34, 0.97);
                border-radius: 18px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                padding: 40px;
                width: 600px;
                margin-bottom: 30px;
            }
            .export-title {
                color: #00eaff;
                font-size: 2.2rem;
                font-weight: bold;
                margin-bottom: 32px;
                letter-spacing: 2px;
                text-shadow: 0 0 10px #00eaff44;
                text-align: center;
            }
            .export-form {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            .export-form select {
                padding: 12px;
                border-radius: 8px;
                border: none;
                background: #232526;
                color: #fff;
                font-size: 1.1rem;
                outline: none;
            }
            .export-form button {
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
                background: linear-gradient(90deg, #00eaff 0%, #005bea 100%);
                color: #fff;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                letter-spacing: 1px;
            }
            .links {
                margin-top: 22px;
                text-align: center;
            }
            .links a {
                color: #00eaff;
                text-decoration: none;
                margin: 0 10px;
                font-size: 1.1rem;
            }
        </style>
    </head>
    <body>
        <div class="export-container">
            <div class="export-title">Export Screenshots</div>
            <form class="export-form" action="/export" method="post">
                <select name="category" required>
                    <option value="all">All Categories</option>
                    {''.join(f'<option value="{cat}">{cat}</option>' for cat in app.user_categories[user])}
                </select>
                <button type="submit">Export as ZIP</button>
            </form>
        </div>
        <div class="links">
            <a href="/">Back to Home</a>
            <a href="/view">View Screenshots</a>
        </div>
    </body>
    </html>
    """

@app.post("/export")
async def export_screenshots(request: Request, category: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    
    if not hasattr(app, "screenshots"):
        app.screenshots = {}
    
    # Create a ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_id, info in app.screenshots.items():
            if info["user"] != user:
                continue
            if category != "all" and info["category"] != category:
                continue
            
            file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{info['filename']}")
            if os.path.exists(file_path):
                # Add file to ZIP with category as subfolder
                zip_file.write(file_path, f"{info['category']}/{info['filename']}")
    
    # Prepare the response
    zip_buffer.seek(0)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return FileResponse(
        zip_buffer,
        media_type="application/zip",
        filename=f"screenshots_{category}_{timestamp}.zip"
    )

@app.get("/delete", response_class=HTMLResponse)
async def delete_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    
    if not hasattr(app, "screenshots"):
        app.screenshots = {}
    
    user_screenshots = {k: v for k, v in app.screenshots.items() if v["user"] == user}
    screenshots_html = ""
    for file_id, info in user_screenshots.items():
        screenshots_html += f"""
        <div class="screenshot-item">
            <img src='/image/{file_id}_{info["filename"]}' width='200'><br>
            <p>Category: {info["category"]}</p>
            <form action="/delete" method="post" style="display: inline;">
                <input type="hidden" name="file_id" value="{file_id}">
                <button type="submit" onclick="return confirm('Are you sure you want to delete this screenshot?')">Delete</button>
            </form>
        </div>
        """
    
    return f"""
    <html>
    <head>
        <title>Delete Screenshots - Smart Screenshot Manager</title>
        <style>
            body {{
                background: linear-gradient(135deg, #232526 0%, #414345 100%);
                min-height: 100vh;
                margin: 0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
            }}
            .delete-container {{
                background: rgba(30, 32, 34, 0.97);
                border-radius: 18px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                padding: 40px;
                width: 800px;
            }}
            .delete-title {{
                color: #00eaff;
                font-size: 2.2rem;
                font-weight: bold;
                margin-bottom: 32px;
                letter-spacing: 2px;
                text-shadow: 0 0 10px #00eaff44;
                text-align: center;
            }}
            .screenshot-item {{
                background: rgba(35, 37, 38, 0.97);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                text-align: center;
            }}
            .screenshot-item img {{
                border-radius: 4px;
                margin-bottom: 10px;
            }}
            .screenshot-item p {{
                color: #fff;
                margin: 10px 0;
            }}
            .screenshot-item button {{
                padding: 8px 16px;
                border-radius: 8px;
                border: none;
                background: #ff4444;
                color: #fff;
                font-size: 1rem;
                cursor: pointer;
            }}
            .screenshot-item button:hover {{
                background: #ff0000;
            }}
            .links {{
                margin-top: 22px;
                text-align: center;
            }}
            .links a {{
                color: #00eaff;
                text-decoration: none;
                margin: 0 10px;
                font-size: 1.1rem;
            }}
        </style>
    </head>
    <body>
        <div class="delete-container">
            <div class="delete-title">Delete Screenshots</div>
            {screenshots_html}
        </div>
        <div class="links">
            <a href="/">Back to Home</a>
            <a href="/view">View Screenshots</a>
        </div>
    </body>
    </html>
    """

@app.post("/delete")
async def delete_screenshot(request: Request, file_id: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    
    if not hasattr(app, "screenshots") or file_id not in app.screenshots or app.screenshots[file_id]["user"] != user:
        return HTMLResponse("Screenshot not found.", status_code=404)
    
    # Delete file from storage
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{app.screenshots[file_id]['filename']}")
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove from app.screenshots
    del app.screenshots[file_id]
    
    return RedirectResponse("/delete", status_code=303)

@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    
    if not hasattr(app, "screenshots"):
        app.screenshots = {}
    
    # Get user's screenshots
    user_screenshots = {k: v for k, v in app.screenshots.items() if v["user"] == user}
    
    # Calculate statistics
    category_stats = Counter(info["category"] for info in user_screenshots.values())
    label_stats = Counter()
    for info in user_screenshots.values():
        if "analysis" in info and "labels" in info["analysis"]:
            label_stats.update(info["analysis"]["labels"])
    
    # Generate HTML for statistics
    stats_html = f"""
    <div class="stats-section">
        <h3>Category Distribution</h3>
        <div class="stats-grid">
            {''.join(f'''
            <div class="stat-item">
                <div class="stat-label">{cat}</div>
                <div class="stat-value">{count}</div>
            </div>
            ''' for cat, count in category_stats.most_common())}
        </div>
    </div>
    
    <div class="stats-section">
        <h3>Top Labels</h3>
        <div class="stats-grid">
            {''.join(f'''
            <div class="stat-item">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{count}</div>
            </div>
            ''' for label, count in label_stats.most_common(10))}
        </div>
    </div>
    """
    
    return f"""
    <html>
    <head>
        <title>Statistics - Smart Screenshot Manager</title>
        <style>
            body {{
                background: linear-gradient(135deg, #232526 0%, #414345 100%);
                min-height: 100vh;
                margin: 0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
            }}
            .stats-container {{
                background: rgba(30, 32, 34, 0.97);
                border-radius: 18px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                padding: 40px;
                width: 800px;
            }}
            .stats-title {{
                color: #00eaff;
                font-size: 2.2rem;
                font-weight: bold;
                margin-bottom: 32px;
                letter-spacing: 2px;
                text-shadow: 0 0 10px #00eaff44;
                text-align: center;
            }}
            .stats-section {{
                margin-bottom: 40px;
            }}
            .stats-section h3 {{
                color: #00eaff;
                margin-bottom: 20px;
                text-align: center;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 20px;
            }}
            .stat-item {{
                background: rgba(35, 37, 38, 0.97);
                border-radius: 8px;
                padding: 15px;
                text-align: center;
            }}
            .stat-label {{
                color: #fff;
                font-size: 1.1rem;
                margin-bottom: 5px;
            }}
            .stat-value {{
                color: #00eaff;
                font-size: 1.5rem;
                font-weight: bold;
            }}
            .links {{
                margin-top: 22px;
                text-align: center;
            }}
            .links a {{
                color: #00eaff;
                text-decoration: none;
                margin: 0 10px;
                font-size: 1.1rem;
            }}
        </style>
    </head>
    <body>
        <div class="stats-container">
            <div class="stats-title">Screenshot Statistics</div>
            {stats_html}
        </div>
        <div class="links">
            <a href="/">Back to Home</a>
            <a href="/view">View Screenshots</a>
        </div>
    </body>
    </html>
    """
