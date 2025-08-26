// frontend/src/UploadForm.js
import React, { useState } from "react";
import axios from "axios";

const UploadForm = () => {
  const [tags, setTags] = useState("");
  const [files, setFiles] = useState([]);
  const [message, setMessage] = useState("");
  const [results, setResults] = useState({});

  const handleFileChange = (e) => {
    setFiles([...e.target.files]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!files.length) {
      setMessage("Please upload at least one image.");
      return;
    }

    const formData = new FormData();
    formData.append("keywords", tags);
    files.forEach((f) => formData.append("files", f));

    try {
      setMessage("Uploading and clustering images...");
      const response = await axios.post(
        "http://127.0.0.1:8000/cluster/by_keywords/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      if (response.data.status === "ok") {
        setResults(response.data.grouped);
        setMessage(`Successfully clustered ${response.data.assignments_count} images.`);
      } else {
        setMessage("Error: " + response.data.detail);
      }
    } catch (error) {
      console.error(error);
      setMessage("Error uploading files.");
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto bg-white shadow-md rounded-lg">
      <h1 className="text-2xl font-bold mb-4">Smart Screenshot Organizer</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Enter tags (comma separated)"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          className="w-full p-2 border rounded"
        />

        <input
          type="file"
          onChange={handleFileChange}
          multiple
          className="w-full"
        />

        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Upload & Cluster
        </button>
      </form>

      {message && <p className="mt-4 text-green-600">{message}</p>}

      {Object.keys(results).length > 0 && (
        <div className="mt-6">
          {Object.keys(results).map((kw) => (
            <div key={kw}>
              <h2 className="font-bold text-xl mt-4">{kw}</h2>
              <div className="flex flex-wrap gap-4 mt-2">
                {results[kw].map((img) => (
                  <img
                    key={img.file_name}
                    src={`http://127.0.0.1:8000/results/${kw}/${img.file_name}`}
                    alt={img.file_name}
                    className="w-32 h-32 object-cover rounded"
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UploadForm;
