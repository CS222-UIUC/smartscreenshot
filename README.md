# Smart Screenshot Manager

A smart screenshot management system that helps users organize, categorize, and search their screenshots efficiently.

## Features

### **Completed Features**

1. **User Management**
   - User registration
   - User login/logout
   - Session management
   - Basic permission control

2. **Screenshot Management**
   - Single and batch upload
   - Screenshot preview
   - Edit descriptions
   - Delete screenshots
   - Drag and drop upload

3. **Category Management**
   - Predefined categories
   - Manual categorization
   - Category statistics
   - Category filtering
   - Categories:
     - Work Documents
     - Code Snippets
     - Error Messages
     - Chat Records
     - Web Screenshots
     - System Settings
     - Others

4. **Search Functionality**
   - Description-based search
   - Tag-based search
   - Category-based search
   - Date range search
   - Search history
   - Popular tags

5. **Folder Management**
   - Create folders
   - Delete folders
   - Move screenshots
   - Folder navigation
   - Drag and drop organization

### **Planned Features**

1. **Security Enhancements**
   - Input validation
   - File upload security
   - SQL injection prevention
   - XSS protection
   - CSRF protection

2. **Performance Optimization**
   - Database indexing
   - Query optimization
   - Caching mechanism
   - Concurrent processing
   - Large file handling

3. **Logging System**
   - Operation logs
   - Error logs
   - Access logs
   - Performance monitoring

4. **Testing System**
   - Unit tests
   - Integration tests
   - Performance tests
   - Security tests

5. **Documentation**
   - API documentation
   - Development guide
   - Deployment guide
   - User manual

## Tech Stack

- Backend: Python, FastAPI
- Frontend: HTML, CSS, JavaScript
- Database: Local JSON storage
- File Storage: Local file system

## Project Structure

```
screenshot-backend/
├── app/
│   ├── core/           # Core functionality
│   ├── db/            # Database operations
│   ├── models/        # Data models
│   └── main.py        # Main application
├── uploaded_screenshots/  # Screenshot storage
└── local_db/          # Database files
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/CS222-UIUC/smartscreenshot.git
cd smartscreenshot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
cd screenshot-backend
python -m uvicorn app.main:app --reload
```

4. Access the application:
- Open http://localhost:8000 in your browser

## Running Locally

To run the application locally without Docker:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The application will start at [http://localhost:8080](http://localhost:8080).

## Running with Docker

To run the application inside a Docker container:

```bash
docker build -t smartscreenshot .
docker run -p 8080:8080 smartscreenshot
```

Then open [http://localhost:8080](http://localhost:8080) in your browser.

## Deploying to Google Cloud Run

Deployment is handled automatically with GitHub Actions:

1. Push changes to the `main` branch.
2. GitHub Actions will build and deploy the Docker container to Google Cloud Run.
3. The deployed service URL can be found in the Google Cloud Run console.

## API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- UIUC CS222 Course Team
- FastAPI Community
- All contributors 
