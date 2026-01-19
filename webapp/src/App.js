import React, { useState } from 'react';
import axios from 'axios';
import ParameterForm from './components/ParameterForm';
import STLViewer from './components/STLViewer';
import './App.css';

function App() {
  const [parameters, setParameters] = useState({
    boxLength: 200,
    boxWidth: 150,
    boxHeight: 150,
    wallThickness: 4,
    threadDiameter: 16,
    scraperBaseSize: 28.8,
    spoutPosition: 'left',
    boxColor: '#3498db',
    lidColor: '#e74c3c'
  });

  const [stlUrls, setStlUrls] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);

  const handleParameterChange = (name, value) => {
    setParameters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCreate = async () => {
    setLoading(true);
    setError(null);
    setStlUrls(null);
    setDownloadUrl(null);

    try {
      const response = await axios.post('/api/generate', parameters);

      if (response.data.success) {
        setStlUrls({
          box: `/api/files/${response.data.sessionId}/box.stl`,
          lid: `/api/files/${response.data.sessionId}/lid.stl`
        });
        setDownloadUrl(`/api/download/${response.data.sessionId}`);
      } else {
        setError(response.data.error || 'Generation failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to generate model');
      console.error('Generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (downloadUrl) {
      window.location.href = downloadUrl;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Coffee Grounds Container Designer</h1>
        <p>Customize your 3D-printable coffee grounds compost container</p>
      </header>

      <div className="App-content">
        <div className="left-panel">
          <ParameterForm
            parameters={parameters}
            onChange={handleParameterChange}
            onGenerate={handleCreate}
            loading={loading}
          />

          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}

          {downloadUrl && (
            <button
              className="download-button"
              onClick={handleDownload}
              disabled={loading}
            >
              Download STL Files (ZIP)
            </button>
          )}
        </div>

        <div className="right-panel">
          <STLViewer
            stlUrls={stlUrls}
            boxColor={parameters.boxColor}
            lidColor={parameters.lidColor}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
