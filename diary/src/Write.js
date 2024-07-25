import React, { useState } from 'react';
import './Write.css';
import headerImage from './logo.png';
import { useLocation, useNavigate } from 'react-router-dom';


const Write = () => {
  const [markdownText, setMarkdownText] = useState('');
  const [loading, setLoading] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const userId = location.state?.userId;

  const handleTextChange = (event) => {
    setMarkdownText(event.target.value);
  };

  const handleLogoClick = () => {
    navigate('/main', { state: { userId } });
  };

  const handleSubmit = async () => {
    const requestData = {
      content: markdownText,
      user_id: userId,
      created_at: new Date().toISOString().split('T')[0]
    };

    setLoading(true); // 로딩 시작

    try {
      const response = await fetch('http://172.10.5.46:80/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (response.ok) {
        alert('Request successful');
        // Add any additional actions on success, e.g., navigate to another page
      } else {
        alert('Request failed');
      }
    } catch (error) {
      console.error('Error submitting request:', error);
      alert('Error submitting request');
    }

    setLoading(false); // 로딩 종료
    navigate(-1);
  };

  return (
    <div>
      <div className="inner_header">
        <img 
          src={headerImage}
          alt="Logo" 
          className="header-image" 
          onClick={handleLogoClick} 
          style={{ cursor: 'pointer' }} 
        />
      </div>
      <div className="input-container">
        <textarea 
          placeholder="Content goes here..." 
          value={markdownText} 
          onChange={handleTextChange} 
          className="markdown-input"
        />
        <button onClick={handleSubmit} disabled={loading}>
          {loading ? 'Loading...' : '완료'}
        </button>
      </div>
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner">Loading...</div>
        </div>
      )}
    </div>
  );
};

export default Write;
