import { useState } from "react";
import './Dashboard.css';

export default function Dashboard() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    const response = await fetch("http://localhost:8000/api/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    console.log("Upload response:", data);
  };

  const handleSearch = () => {
    console.log("Searching for:", searchQuery);
    // Later: Add request to search endpoint
  };

  const handleDelete = () => {
    console.log("Delete action triggered");
    // Later: Add request to delete selected or all files
  };

  const handleExport = () => {
    console.log("Export action triggered");
    // Later: Implement export/download of data
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>Screenshot Dashboard</h2>
      </div>

      <div className="dashboard-content">
        <div className="upload-section">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            className="file-input"
          />
          <button onClick={handleUpload} className="button upload-btn">
            Upload
          </button>
        </div>

        <div className="search-section">
          <input
            type="text"
            placeholder="Search images..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <button onClick={handleSearch} className="button search-btn">
            Search
          </button>
        </div>

        <div className="action-buttons">
          <button onClick={handleDelete} className="button delete-btn">
            Delete Images
          </button>
          <button onClick={handleExport} className="button export-btn">
            Export Data
          </button>
        </div>
      </div>
    </div>
  );
}
