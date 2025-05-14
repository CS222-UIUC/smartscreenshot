import { useState } from 'react';
import { uploadScreenshot } from '../api';

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (file) {
      try {
        const response = await uploadScreenshot(file);
        alert('Upload successful');
      } catch (err) {
        alert('Upload failed');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" onChange={e => setFile(e.target.files?.[0] || null)} />
      <button type="submit">Upload Screenshot</button>
    </form>
  );
}