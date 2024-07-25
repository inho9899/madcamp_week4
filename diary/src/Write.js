import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './Write.css';
import headerImage from './logo.png';

const Write = () => {
  const [markdownText, setMarkdownText] = useState('');

  const handleTextChange = (event) => {
    setMarkdownText(event.target.value);
  };

  const handleLogoClick = () => {
    window.location.reload();
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
      <textarea 
            placeholder="Content goes here..." 
            value={markdownText} 
            onChange={handleTextChange} 
            className="markdown-input"
        />
      <footer id="footer">
        <button>완료</button>
      </footer>
    </div>
  );
};

export default Write;
