import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';
import headerImage from './logo.png';

const EditorComponent = () => {
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

      <div className="kakao-editor-container">
        <div className="kakao-editor">
          <textarea 
            placeholder="Content goes here..." 
            value={markdownText} 
            onChange={handleTextChange} 
            className="markdown-input"
          />
          <div className="markdown-preview">
            <ReactMarkdown>{markdownText}</ReactMarkdown>
          </div>
        </div>
      </div>

      <footer id="footer">
        <button>임시저장</button>
        <button>완료</button>
      </footer>
    </div>
  );
};

export default EditorComponent;
