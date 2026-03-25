import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileVideo, Play, MessageSquare, Bot, Send, Loader2, CheckCircle2, ChevronRight, Video, AlertCircle } from 'lucide-react';
import axios from 'axios';
import './index.css';

const API_URL = 'http://localhost:8000/api';

function App() {
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'chat'
  
  // Upload & Process State
  const [files, setFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, success, error
  const [processStatus, setProcessStatus] = useState('idle'); // idle, processing, success, error
  const fileInputRef = useRef(null);
  
  // Chat State
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'ai', content: 'Hello! I am your AI Teaching Assistant. I can answer questions based on the videos you upload and process.', chunks: null }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isTyping]);

  const handleFileSelect = (e) => {
    if (e.target.files?.length > 0) {
      setFiles(Array.from(e.target.files));
      setUploadStatus('idle');
      setProcessStatus('idle');
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploadStatus('uploading');
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadStatus('success');
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadStatus('error');
    }
  };

  const [processStateInfo, setProcessStateInfo] = useState('');

  // Poll for pipeline status
  useEffect(() => {
    let interval;
    if (processStatus === 'processing') {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_URL}/process/status`);
          if (res.data.status === 'success') {
            setProcessStatus('success');
            setProcessStateInfo(res.data.step);
            clearInterval(interval);
          } else if (res.data.status === 'error') {
            setProcessStatus('error');
            setProcessStateInfo(res.data.step);
            clearInterval(interval);
          } else {
            setProcessStateInfo(res.data.step);
          }
        } catch (e) {
          console.error(e);
        }
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [processStatus]);

  const handleProcess = async () => {
    setProcessStatus('processing');
    setProcessStateInfo('Waking up pipeline...');
    try {
      await axios.post(`${API_URL}/process`);
      // Once triggered, the useEffect polling kicks in
    } catch (error) {
      console.error('Processing failed:', error);
      setProcessStatus('error');
      setProcessStateInfo('Failed to start pipeline');
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!query.trim() || isTyping) return;

    const userQuery = query.trim();
    setQuery('');
    setChatHistory(prev => [...prev, { role: 'user', content: userQuery }]);
    setIsTyping(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, { query: userQuery, top_k: 3 });
      
      setChatHistory(prev => [...prev, { 
        role: 'ai', 
        content: response.data.answer,
        chunks: response.data.chunks
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      setChatHistory(prev => [...prev, { 
        role: 'ai', 
        content: error.response?.data?.detail || 'Sorry, I encountered an error answering your question. Make sure your local LLM is running and videos are processed.',
        isError: true
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="app-container">
      <motion.header 
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="header"
      >
        <h1 className="text-gradient">AI Teaching Assistant</h1>
        <p>Upload video lectures, process them, and ask intelligent questions.</p>
      </motion.header>

      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginBottom: '1rem' }}>
        <button 
          onClick={() => setActiveTab('upload')} 
          className={`btn ${activeTab === 'upload' ? 'btn-primary' : ''}`}
        >
          <Video size={18} /> Manage Videos
        </button>
        <button 
          onClick={() => setActiveTab('chat')} 
          className={`btn ${activeTab === 'chat' ? 'btn-primary' : ''}`}
        >
          <MessageSquare size={18} /> Chat Assistant
        </button>
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'upload' ? (
          <motion.div 
            key="upload-panel"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
            className="grid-layout"
          >
            {/* Upload Section */}
            <div className="glass-panel">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Upload size={24} className="text-gradient" /> Upload Videos
              </h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                Select MP4 files to add to your knowledge base.
              </p>
              
              <div 
                className={`upload-zone ${files.length > 0 ? 'active' : ''}`}
                onClick={() => fileInputRef.current?.click()}
              >
                <input 
                  type="file" 
                  accept=".mp4" 
                  multiple 
                  ref={fileInputRef} 
                  onChange={handleFileSelect} 
                  style={{ display: 'none' }} 
                />
                <FileVideo size={48} color={files.length > 0 ? 'var(--accent)' : 'var(--text-secondary)'} style={{ margin: '0 auto 1rem' }} />
                <h3>Click to browse or drag and drop</h3>
                <p style={{ color: 'var(--text-secondary)' }}>MP4 format only</p>
              </div>

              {files.length > 0 && (
                <div className="file-list">
                  {files.map((file, i) => (
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} key={i} className="file-item">
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <FileVideo size={18} /> {file.name}
                      </span>
                      <span className="badge">{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                    </motion.div>
                  ))}
                  
                  <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
                    <button 
                      className="btn btn-primary" 
                      onClick={handleUpload}
                      disabled={uploadStatus === 'uploading' || uploadStatus === 'success'}
                    >
                      {uploadStatus === 'uploading' ? <><Loader2 className="spinner" size={18} /> Uploading...</> : 
                       uploadStatus === 'success' ? <><CheckCircle2 size={18} /> Uploaded</> : 
                       'Upload Files'}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Process Section */}
            <div className="glass-panel">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Play size={24} className="text-gradient" /> Pipeline Status
              </h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                Extract audio, transcribe via Whisper, and create vector embeddings via Ollama.
              </p>

              <div className="process-steps">
                <div className={`step-item ${uploadStatus === 'success' ? 'active' : ''}`}>
                  <div className="icon-container">
                    {uploadStatus === 'success' ? <CheckCircle2 color="var(--success)" /> : <div className="circle-placeholder"></div>}
                  </div>
                  <div>
                    <h4>1. Video Upload</h4>
                    <span className="badge">MP4 saved to server</span>
                  </div>
                </div>
                
                <div className={`step-item ${processStatus === 'processing' ? 'active' : processStatus === 'success' ? 'completed' : processStatus === 'error' ? 'error' : ''}`} style={{ borderColor: processStatus === 'error' ? 'rgba(239, 68, 68, 0.3)' : undefined, flexDirection: 'column', alignItems: 'stretch' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div className="icon-container">
                      {processStatus === 'processing' ? <Loader2 className="spinner" color="var(--accent)" /> : 
                       processStatus === 'success' ? <CheckCircle2 color="var(--success)" /> : 
                       processStatus === 'error' ? <AlertCircle color="var(--danger)" /> :
                       <div className="circle-placeholder"></div>}
                    </div>
                    <div>
                      <h4>2. Extract, Transcribe & Embed</h4>
                      <span className="badge" style={{ color: processStatus === 'error' ? 'var(--danger)' : undefined }}>
                        {processStateInfo || 'Running Backend ML Pipeline'}
                      </span>
                    </div>
                  </div>
                  
                  {processStatus === 'processing' && (
                    <div style={{ marginTop: '1rem', padding: '0 0.5rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                        <span>Progress (Estimated)</span>
                        <span>Please wait... (~2-5 mins)</span>
                      </div>
                      <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                        <motion.div 
                          initial={{ width: "0%" }}
                          animate={{ width: "95%" }}
                          transition={{ duration: 180, ease: "easeOut" }} // 3 minute synthetic loading
                          style={{ height: '100%', background: 'var(--accent)' }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div style={{ marginTop: '2rem' }}>
                <button 
                  className="btn btn-primary" 
                  style={{ width: '100%', background: processStatus === 'error' ? 'var(--danger)' : undefined, borderColor: processStatus === 'error' ? 'var(--danger)' : undefined }}
                  onClick={handleProcess}
                  disabled={processStatus === 'processing' || uploadStatus !== 'success'}
                >
                  {processStatus === 'processing' ? <><Loader2 className="spinner" size={18} /> Processing Background Job...</> : 
                   processStatus === 'success' ? <><CheckCircle2 size={18} /> Pipeline Ready</> : 
                   processStatus === 'error' ? <><AlertCircle size={18} /> Retry Processing</> :
                   'Start Processing'}
                </button>
                {processStatus === 'success' && (
                  <p style={{ color: 'var(--success)', textAlign: 'center', marginTop: '1rem', fontSize: '0.9rem' }}>
                    Embeddings created successfully. You can now use the Chat Assistant.
                  </p>
                )}
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="chat-panel"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="glass-panel chat-container"
          >
            <div className="messages">
              {chatHistory.map((msg, idx) => (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  key={idx} 
                  className={`message ${msg.role}`}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
                    <div className="avatar" style={{ background: msg.role === 'user' ? 'var(--accent)' : 'rgba(255,255,255,0.1)', padding: '0.5rem', borderRadius: '50%' }}>
                      {msg.role === 'user' ? <MessageSquare size={20} color="white" /> : <Bot size={20} className="text-gradient" />}
                    </div>
                    
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                      <div className="message-bubble">
                        {msg.content}
                      </div>

                      {msg.chunks && msg.chunks.length > 0 && (
                        <div className="source-cards" style={{ width: '100%', minWidth: '300px' }}>
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Sources Referenced</span>
                          {msg.chunks.map((chunk, cIdx) => (
                            <div key={cIdx} className="source-card">
                              <div className="source-card-header">
                                <span className="source-card-title"><Video size={14} /> {chunk.title} {chunk.number ? `(Part ${chunk.number})` : ''}</span>
                                <span className="badge">{(chunk.score * 100).toFixed(0)}% match</span>
                              </div>
                              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                                Timestamp: {Math.floor(chunk.start / 60)}:{Math.floor(chunk.start % 60).toString().padStart(2, '0')} - {Math.floor(chunk.end / 60)}:{Math.floor(chunk.end % 60).toString().padStart(2, '0')}
                              </div>
                              <div style={{ fontStyle: 'italic', opacity: 0.9 }}>"{chunk.text}"</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {isTyping && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="message ai">
                   <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                    <div className="avatar" style={{ background: 'rgba(255,255,255,0.1)', padding: '0.5rem', borderRadius: '50%' }}>
                      <Bot size={20} className="text-gradient" />
                    </div>
                    <div className="message-bubble" style={{ display: 'flex', gap: '4px', alignItems: 'center', height: '44px' }}>
                      <span className="dot-typing"></span><span className="dot-typing"></span><span className="dot-typing"></span>
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={chatEndRef} />
            </div>

            <form className="chat-input-area" onSubmit={handleChat}>
              <input 
                type="text" 
                className="input" 
                placeholder="Ask about your video lectures..." 
                value={query}
                onChange={e => setQuery(e.target.value)}
                disabled={isTyping}
              />
              <button type="submit" className="btn btn-primary" disabled={!query.trim() || isTyping}>
                <Send size={18} />
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
      
      <style>{`
        .dot-typing {
          width: 6px;
          height: 6px;
          background-color: var(--text-primary);
          border-radius: 50%;
          animation: bounce 1.4s infinite ease-in-out both;
        }
        .dot-typing:nth-child(1) { animation-delay: -0.32s; }
        .dot-typing:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }
        .circle-placeholder {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          border: 2px solid rgba(255,255,255,0.2);
        }
      `}</style>
    </div>
  );
}

export default App;
