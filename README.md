# Smart Screenshot Manager

A powerful web application for managing and organizing screenshots using AI-powered analysis.

## Team Members

### Machine Learning Engineer - saketmp2
- Train and fine-tune CNN model for screenshot classification
- Handle data collection and preprocessing
- Integrate ML model with backend API

### Backend Developer - shuwanx2
- Set up FastAPI backend and develop API endpoints
- Manage MongoDB Atlas database
- Implement authentication and integrate Google Photos API

### Frontend Developer - nealb3
- Design and develop React.js frontend interface
- Implement features (upload, category management, search, export, delete)
- Connect frontend with backend APIs

### DevOps & Integration Engineer - yhu74
- Set up and maintain CI/CD pipeline
- Deploy application to Google Cloud Run
- Conduct end-to-end testing and optimize performance

## Features

### Screenshot Management
- **Upload Screenshots**
  - Local storage upload
  - Multiple file upload support
  - Category selection during upload

- **View Screenshots**
  - Browse screenshots by category
  - View classification information
  - Display analysis results

- **Edit Categories**
  - Modify screenshot categories
  - Add custom categories
  - Delete custom categories

### Search and Analysis
- **Content-based Search**
  - Text search using Google Vision API
  - Label-based search
  - Web entity search

- **Export Data**
  - Export as ZIP files
  - Organized by categories
  - Selective category export

- **Delete Screenshots**
  - Individual deletion
  - Confirmation prompts
  - Complete removal from storage and database

- **Statistics**
  - Category distribution
  - Label frequency analysis
  - Visual data representation

## Technical Requirements

- Python 3.7+
- FastAPI
- Google Cloud Vision API
- Required Python packages:
  ```
  fastapi
  uvicorn
  python-multipart
  google-cloud-vision
  ```

## Setup

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd smart-screenshot-manager
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Google Cloud Vision API:
   - Create a Google Cloud project
   - Enable the Vision API
   - Set up service account credentials
   - Update the credentials in the code

4. Run the application backend:
   ```bash
   uvicorn app.main:app --reload
   ```
   
5. Run the application frontend:
   ```bash
   cd screenshot-frontend
   npm run dev
   ```

6. Access the application:
   ```
   http://127.0.0.1:8000 #backend
   http://127.0.0.1:5173/ #frontend
   ```

## Usage

1. **Registration/Login**
   - Create an account or login
   - Access the dashboard

2. **Upload Screenshots**
   - Click "Upload Screenshot"
   - Select files
   - Choose category
   - Submit

3. **Manage Screenshots**
   - View all screenshots
   - Change categories
   - Delete unwanted screenshots

4. **Search and Export**
   - Use search for specific content
   - Export screenshots by category
   - View statistics

## Security

- User authentication required
- Secure session management
- Protected file storage
- API key security

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Cloud Vision API for image analysis
- FastAPI for the web framework
- All contributors and users 
