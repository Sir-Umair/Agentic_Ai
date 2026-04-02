import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';

const ChatNegotiator = ({ onSearchComplete }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! Welcome to our AI-powered premium store. What kind of products are you looking for today?"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMessage,
          history: messages 
        })
      });

      const data = await response.json();
      
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);

      if (data.shouldSearch) {
        setTimeout(() => {
          onSearchComplete(data.searchQuery || userMessage);
        }, 2000);
      }
      
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I'm having trouble connecting to my brain right now." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>Personal AI Shopper</h1>
        <p style={{ color: "var(--text-muted)" }}>Let's find the perfect product for you</p>
      </div>

      <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '1.5rem', overflow: 'hidden' }}>
        <div className="chat-history" ref={scrollRef}>
          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble ${msg.role}`}>
              {msg.role === 'assistant' && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <Sparkles size={16} color="var(--primary)" />
                  <span style={{ fontSize: '0.8rem', fontWeight: 'bold', color: 'var(--primary)' }}>AI Assistant</span>
                </div>
              )}
              {msg.content}
            </div>
          ))}
          {isLoading && (
            <div className="chat-bubble assistant" style={{ opacity: 0.7 }}>
              Thinking...
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="chat-input-area">
          <input 
            type="text" 
            placeholder="E.g., I'm looking for a premium gaming laptop under $2000..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
          />
          <button type="submit" className="chat-submit-btn" disabled={isLoading || !input.trim()}>
            <Send size={24} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatNegotiator;
