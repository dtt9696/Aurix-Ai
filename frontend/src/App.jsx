import React, { useState, useRef, useEffect } from 'react';
import { Search, ShieldAlert, FileText, Activity, Bell, ChevronRight, TrendingDown, TrendingUp, CheckCircle, Info, ExternalLink, RefreshCw, BarChart2, PieChart, Layers, History, Play, Upload, MessageSquare } from 'lucide-react';

const App = () => {
  const [input, setInput] = useState('');
  const [scenario, setScenario] = useState('');
  const [feedback, setFeedback] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Welcome to RiskAgent Pro Elite. I am now equipped with Multi-modal OCR, Persistent Memory, and Self-Correction loops.' }
  ]);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [activeTab, setActiveTab] = useState('home'); 
  const [sessionId] = useState(`session-${Math.random().toString(36).substr(2, 9)}`);
  
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    if (report && window.echarts) {
      const chartContainers = document.querySelectorAll('.chart-container');
      chartContainers.forEach(container => {
        const configStr = container.getAttribute('data-config');
        if (configStr) {
          try {
            const config = JSON.parse(configStr.replace(/'/g, '"'));
            const chart = window.echarts.init(container);
            chart.setOption(config.config);
          } catch (e) {
            console.error('Failed to render chart:', e);
          }
        }
      });
    }
  }, [report]);

  const extractHtml = (text) => {
    if (!text) return null;
    const htmlMatch = text.match(/```html\s+([\s\S]*?)\s+```/i) || text.match(/```\s+([\s\S]*?)\s+```/i);
    if (htmlMatch) return htmlMatch[1];
    return null;
  };

  const cleanMessage = (text) => {
    if (!text) return '';
    return text.replace(/```html\s+[\s\S]*?\s+```/i, '').replace(/```\s+[\s\S]*?\s+```/i, '').trim();
  };

  const handleSubmit = async (e, forcedInput = null, type = 'chat') => {
    if (e) e.preventDefault();
    const query = forcedInput || (type === 'feedback' ? feedback : input);
    if (!query.trim()) return;

    let fullQuery = query;
    if (type === 'feedback') {
        fullQuery = `[USER FEEDBACK FOR CALIBRATION] ${query}`;
        setFeedback('');
    } else if (scenario) {
        fullQuery = `[Scenario: ${scenario}] ${query}`;
    }

    const userMessage = { role: 'user', content: fullQuery };
    setMessages(prev => [...prev, userMessage]);
    if (type !== 'feedback') setInput('');
    setLoading(true);
    setActiveTab('chat');

    try {
      const response = await fetch('/agents/risk_analyzer/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: fullQuery,
          session_id: sessionId
        })
      });

      if (!response.ok) throw new Error('Failed to connect to agent');

      const data = await response.json();
      const agentText = data.output || 'No response from agent.';
      const extractedHtml = extractHtml(agentText);
      const cleanedText = cleanMessage(agentText);

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: cleanedText || (extractedHtml ? 'Analysis complete. Report generated.' : 'Processing complete.'), 
        reportData: extractedHtml 
      }]);
      
      if (extractedHtml) {
        setReport(extractedHtml);
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error: Connection lost. Re-authenticating with the risk engine...' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#000', color: '#fff', fontFamily: 'Inter, sans-serif', overflow: 'hidden' }}>
      {/* Sidebar */}
      <div style={{ width: '300px', background: '#0a0a0a', borderRight: '1px solid #222', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '40px 32px', borderBottom: '1px solid #222' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', fontWeight: '900', fontSize: '1.5rem', color: '#d4af37' }}>
            <ShieldAlert size={20} /> RiskAgent <span style={{ color: '#fff' }}>Elite</span>
          </div>
        </div>
        
        <nav style={{ flex: 1, padding: '32px 20px' }}>
          <h4 style={{ fontSize: '0.7rem', fontWeight: '800', color: '#444', textTransform: 'uppercase', letterSpacing: '0.15em', marginBottom: '24px', paddingLeft: '16px' }}>Intelligence Suite</h4>
          {[
            { id: 'home', label: 'Dashboard', icon: <History size={18} /> },
            { id: 'chat', label: 'Scenario Lab', icon: <Play size={18} /> },
            { id: 'memory', label: 'User Context', icon: <MessageSquare size={18} /> }
          ].map(item => (
            <div key={item.id} onClick={() => { setActiveTab(item.id); setReport(null); }}
              style={{ padding: '14px 20px', background: activeTab === item.id ? 'linear-gradient(90deg, rgba(212, 175, 55, 0.1) 0%, transparent 100%)' : 'transparent', color: activeTab === item.id ? '#d4af37' : '#888', borderRadius: '12px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '14px', fontWeight: activeTab === item.id ? '700' : '500', borderLeft: activeTab === item.id ? '4px solid #d4af37' : '4px solid transparent' }}>
              {item.icon} {item.label}
            </div>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'radial-gradient(circle at top right, #111, #000)' }}>
        <header style={{ height: '80px', background: 'rgba(10, 10, 10, 0.8)', borderBottom: '1px solid #222', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 40px' }}>
           <div style={{ fontWeight: '700', fontSize: '1rem', color: '#d4af37' }}>
             {activeTab === 'home' ? 'Quantum Overview' : activeTab === 'chat' ? 'Simulation Lab' : 'Memory Calibration'}
           </div>
           <div style={{ display: 'flex', gap: '16px' }}>
              <button style={{ background: '#111', border: '1px solid #333', borderRadius: '10px', padding: '8px 16px', fontSize: '0.8rem', color: '#888', cursor: 'pointer' }}><Upload size={14} style={{ marginRight: '8px' }} /> Upload PDF</button>
           </div>
        </header>

        <main style={{ flex: 1, overflowY: 'auto', padding: '48px' }}>
          {activeTab === 'memory' ? (
            <div style={{ maxWidth: '700px', margin: '0 auto' }}>
                <h2 style={{ color: '#d4af37', marginBottom: '24px' }}>Calibration & Feedback</h2>
                <p style={{ color: '#888', marginBottom: '32px' }}>Your feedback directly adjusts the agent's risk tolerance and predictive calibration factor.</p>
                <div style={{ background: '#0a0a0a', padding: '32px', borderRadius: '24px', border: '1px solid #222' }}>
                    <textarea 
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        placeholder="e.g., 'The last iRobot prediction was too safe' or 'Prioritize liquidity risks'" 
                        style={{ width: '100%', height: '120px', background: '#111', border: '1px solid #333', borderRadius: '16px', color: '#fff', padding: '16px', outline: 'none', marginBottom: '24px' }}
                    />
                    <button onClick={(e) => handleSubmit(e, null, 'feedback')} style={{ width: '100%', padding: '16px', background: '#d4af37', color: '#000', fontWeight: '800', border: 'none', borderRadius: '12px', cursor: 'pointer' }}>Calibrate Engine</button>
                </div>
            </div>
          ) : (
            <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', gap: '40px', height: 'calc(100vh - 220px)' }}>
                <div style={{ flex: report ? '1' : '1', display: 'flex', flexDirection: 'column', background: '#0a0a0a', borderRadius: '32px', border: '1px solid #222', overflow: 'hidden' }}>
                  <div style={{ flex: 1, overflowY: 'auto', padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {messages.map((m, i) => (
                      <div key={i} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '85%' }}>
                        <div style={{ padding: '18px 24px', borderRadius: m.role === 'user' ? '24px 24px 4px 24px' : '24px 24px 24px 4px', background: m.role === 'user' ? '#d4af37' : '#1a1a1a', color: m.role === 'user' ? '#000' : '#fff', fontWeight: m.role === 'user' ? '700' : '500' }}>
                          {m.content}
                          {m.reportData && !report && (
                            <button onClick={() => setReport(m.reportData)} style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '16px', padding: '12px', background: '#000', border: '1px solid #d4af37', borderRadius: '12px', cursor: 'pointer', color: '#d4af37', width: '100%', fontWeight: '800' }}>
                              <BarChart2 size={18} /> Open Visual Report
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                    {loading && <div className="pulse-loader"></div>}
                    <div ref={messagesEndRef} />
                  </div>
                  
                  <div style={{ padding: '24px 32px', borderTop: '1px solid #222', background: '#0a0a0a' }}>
                    <div style={{ marginBottom: '16px' }}>
                      <input value={scenario} onChange={(e) => setScenario(e.target.value)} placeholder="Scenario (e.g., '10% tariff increase')" style={{ width: '100%', padding: '12px 20px', borderRadius: '12px', background: '#111', border: '1px solid #333', color: '#fff', fontSize: '0.8rem', outline: 'none' }} />
                    </div>
                    <form onSubmit={handleSubmit} style={{ position: 'relative' }}>
                      <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Company / PDF Path" style={{ width: '100%', padding: '18px 60px 18px 24px', borderRadius: '18px', background: '#111', border: '1px solid #333', color: '#fff', outline: 'none' }} />
                      <button type="submit" style={{ position: 'absolute', right: '10px', top: '10px', background: '#d4af37', color: '#000', border: 'none', width: '44px', height: '44px', borderRadius: '14px', cursor: 'pointer' }}><Search size={22} /></button>
                    </form>
                  </div>
                </div>

                {report && (
                  <div style={{ flex: '2', display: 'flex', flexDirection: 'column', background: '#fff', borderRadius: '32px', border: '1px solid #d4af37', overflow: 'hidden' }}>
                    <div style={{ padding: '24px 32px', background: '#111', color: '#d4af37', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontWeight: '900' }}><FileText size={22} /> QUANTUM AUDIT DOSSIER</div>
                      <button onClick={() => setReport(null)} style={{ background: 'transparent', border: '1px solid #444', color: '#888', borderRadius: '10px', padding: '8px 16px', cursor: 'pointer' }}>CLOSE</button>
                    </div>
                    <div style={{ flex: 1, overflowY: 'auto', padding: '40px', color: '#000' }}>
                      <div className="report-content" dangerouslySetInnerHTML={{ __html: report }} />
                    </div>
                  </div>
                )}
            </div>
          )}
        </main>
      </div>

      <style>{`
        .chart-container { width: 100%; height: 350px; margin: 32px 0; border: 1px solid #eee; border-radius: 16px; }
        .pulse-loader { width: 24px; height: 24px; border-radius: 50%; background: #d4af37; animation: pulse 1.5s infinite; }
        @keyframes pulse {
          0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.7); }
          70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(212, 175, 55, 0); }
          100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); }
        }
        .report-content h1 { font-size: 2.25rem; font-weight: 900; border-bottom: 4px solid #d4af37; padding-bottom: 16px; margin-bottom: 32px; }
        .report-content strong { color: #d4af37; font-weight: 800; }
      `}</style>
    </div>
  );
};

export default App;
