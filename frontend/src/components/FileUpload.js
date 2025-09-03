import React, { useState, useEffect } from 'react';
import { uploadDocument, getSupportedFormats } from '../services/api';

const FileUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [supportedFormats, setSupportedFormats] = useState([]);
  const [formatDescriptions, setFormatDescriptions] = useState({});

  // Load supported formats on component mount
  useEffect(() => {
    const loadSupportedFormats = async () => {
      try {
        const response = await getSupportedFormats();
        setSupportedFormats(response.supported_formats);
        setFormatDescriptions(response.format_descriptions);
      } catch (error) {
        console.error('Error loading supported formats:', error);
        // Fallback to basic formats
        setSupportedFormats(['.pdf', '.docx', '.txt']);
      }
    };
    
    loadSupportedFormats();
  }, []);

  const isValidFileType = (file) => {
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    return supportedFormats.includes(fileExtension);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && isValidFileType(selectedFile)) {
      setFile(selectedFile);
    } else {
      alert(`Please select a supported file format: ${supportedFormats.join(', ')}`);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && isValidFileType(droppedFile)) {
      setFile(droppedFile);
    } else {
      alert(`Please drop a supported file format: ${supportedFormats.join(', ')}`);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file first');
      return;
    }

    setLoading(true);
    try {
      const response = await uploadDocument(file);
      onUploadSuccess(response, file);  // Pass both response and file
      setFile(null);
      // Reset file input
      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';
    } catch (error) {
      console.error('Upload error:', error);
      alert('Error uploading file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getFileIcon = (filename) => {
    const extension = '.' + filename.split('.').pop().toLowerCase();
    
    const iconColors = {
      '.pdf': 'text-red-600',
      '.docx': 'text-blue-600',
      '.doc': 'text-blue-600',
      '.pptx': 'text-orange-600',
      '.ppt': 'text-orange-600',
      '.xlsx': 'text-green-600',
      '.xls': 'text-green-600',
      '.txt': 'text-gray-600',
      '.rtf': 'text-purple-600',
      '.md': 'text-gray-800',
      '.csv': 'text-green-700'
    };
    
    return iconColors[extension] || 'text-gray-600';
  };

  return (
    <div>
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragOver
            ? 'border-purple-500 bg-purple-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="space-y-3">
          <div className="text-gray-600">
            <svg
              className="mx-auto h-10 w-10 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div>
            <p className="font-medium text-gray-900">
              Drop your document here
            </p>
            <p className="text-sm text-gray-500">
              Supports: PDF, DOCX, PPTX, TXT, RTF, Excel & more
            </p>
            {supportedFormats.length > 0 && (
              <p className="text-xs text-gray-400 mt-1">
                {supportedFormats.join(', ')}
              </p>
            )}
          </div>
          <input
            id="file-input"
            type="file"
            accept={supportedFormats.join(',')}
            onChange={handleFileChange}
            className="hidden"
          />
          <label
            htmlFor="file-input"
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-purple-700 bg-purple-100 hover:bg-purple-200 cursor-pointer"
          >
            Browse Files
          </label>
        </div>
      </div>

      {file && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center min-w-0 flex-1">
              <svg
                className={`h-6 w-6 flex-shrink-0 ${getFileIcon(file.name)}`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M4 18h12V6l-4-4H4v16zm8-14v4h4l-4-4z" />
              </svg>
              <div className="ml-2 min-w-0 flex-1">
                <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                <p className="text-xs text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                  {formatDescriptions['.' + file.name.split('.').pop().toLowerCase()] && 
                    ` • ${formatDescriptions['.' + file.name.split('.').pop().toLowerCase()]}`
                  }
                </p>
              </div>
            </div>
            <button
              onClick={handleUpload}
              disabled={loading}
              className="ml-3 inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-2 h-3 w-3 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Processing...
                </>
              ) : (
                'Upload'
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
