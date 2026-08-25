import React, { useState } from 'react';
import { Send, CornerDownLeft, Sparkles, AlertCircle } from 'lucide-react';

export default function ChatInterface({ config }) {
  const [queryInput, setQueryInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: 'agent',
      headline: 'Executive Business Intelligence Assistant',
      summary_insights: [
        'Query business performance across Work Orders and Deals boards in real time.',
        'Data Resilience Engine normalizes missing values, date formats, and sector categories.'
      ],
      key_metrics: {},
      caveats: [
        'Data Resilience: 181 deals missing value fields imputed to ₹0 for safe aggregations.',
        '34 work orders verified with unbilled status backlog.'
      ],
      suggested_followups: [
        'How is our pipeline looking for energy sector this quarter?',
        'What is our overall revenue and billing status?',
        'Which work orders are currently marked as STUCK?',
        'How are BD owners performing?'
      ]
    }
  ]);

  const handleSendQuery = async (queryText) => {
    const textToSend = queryText || queryInput;
    if (!textToSend.trim() || loading) return;

    const newMessages = [...messages, { sender: 'user', text: textToSend }];
    setMessages(newMessages);
    if (!queryText) setQueryInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: textToSend,
          api_token: config.apiToken,
          deals_board_id: config.dealsBoardId,
          wo_board_id: config.woBoardId
        })
      });
      const data = await res.json();
      setMessages([...newMessages, { sender: 'agent', ...data }]);
    } catch (err) {
      setMessages([...newMessages, {
        sender: 'agent',
        headline: 'Query Execution Error',
        summary_insights: ['Failed to connect to backend API server.'],
        caveats: ['Endpoint /api/query unreachable'],
        suggested_followups: ['Retry query']
      }]);
    } finally {
      setLoading(false);
    }
  };

  const renderSimpleChart = (chart) => {
    if (!chart || !chart.labels || !chart.values) return null;
    const maxVal = Math.max(...chart.values, 1);

    return (
      <div style={{
        marginTop: '16px',
        padding: '16px',
        background: 'var(--bg-app)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-color-subtle)'
      }}>
        <div style={{ fontSize: '0.825rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '12px' }}>
          {chart.title}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {chart.labels.map((label, idx) => {
            const val = chart.values[idx] || 0;
            const pct = Math.min(100, Math.max(6, (val / maxVal) * 100));
            return (
              <div key={idx} style={{ fontSize: '0.78rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', color: 'var(--text-muted)' }}>
                  <span>{label}</span>
                  <span className="tabular-nums" style={{ fontWeight: 700, color: 'var(--text-main)' }}>
                    {typeof val === 'number' ? (val > 10000000 ? `₹${(val/1e7).toFixed(2)} Cr` : val > 100000 ? `₹${(val/1e5).toFixed(2)} L` : val > 1000 ? `₹${val.toLocaleString()}` : val) : val}
                  </span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'var(--bg-surface-elevated)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${pct}%`,
                    height: '100%',
                    background: idx % 2 === 0 ? 'linear-gradient(90deg, #38bdf8 0%, #3b82f6 100%)' : 'linear-gradient(90deg, #10b981 0%, #06b6d4 100%)',
                    borderRadius: '3px',
                    transition: 'width 0.4s ease-out'
                  }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Quick Prompts Bar */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        {[
          "Pipeline by sector",
          "Revenue & billing status",
          "Stuck work orders",
          "BD owner performance",
          "Probability-weighted pipeline"
        ].map((prompt, i) => (
          <button
            key={i}
            id={`preset-btn-${i}`}
            className="btn btn-chip"
            onClick={() => handleSendQuery(prompt)}
          >
            <Sparkles size={13} color="var(--accent-cyan)" />
            <span>{prompt}</span>
          </button>
        ))}
      </div>

      {/* Messages Stream */}
      <div style={{
        minHeight: '380px',
        maxHeight: '540px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        paddingRight: '2px'
      }}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className="fade-in"
            style={{
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: msg.sender === 'user' ? '75%' : '100%',
              width: msg.sender === 'agent' ? '100%' : 'auto'
            }}
          >
            {msg.sender === 'user' ? (
              <div style={{
                background: 'linear-gradient(135deg, #1d263b 0%, #171e30 100%)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-main)',
                padding: '10px 18px',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.88rem',
                fontWeight: 500,
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
              }}>
                {msg.text}
              </div>
            ) : (
              <div className="panel" style={{ padding: '20px', borderLeft: '4px solid var(--accent-cyan)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>{msg.headline || 'Summary'}</h4>
                  {msg.data_source && (
                    <span className="badge badge-cyan" style={{ fontSize: '0.68rem' }}>{msg.data_source}</span>
                  )}
                </div>

                {/* Summary Insights */}
                {msg.summary_insights && msg.summary_insights.length > 0 && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '14px' }}>
                    {msg.summary_insights.map((insight, i) => {
                      const parts = insight.split(/(\*\*.*?\*\*)/g);
                      return (
                        <div key={i} style={{ fontSize: '0.88rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                          {parts.map((p, pIdx) => {
                            if (p.startsWith('**') && p.endsWith('**')) {
                              return <strong key={pIdx} style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>{p.slice(2, -2)}</strong>;
                            }
                            return p;
                          })}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Chart Visualization */}
                {renderSimpleChart(msg.chart)}

                {/* Resilience Audit Notes */}
                {msg.caveats && msg.caveats.length > 0 && (
                  <div style={{
                    marginTop: '14px',
                    padding: '10px 14px',
                    background: 'var(--accent-amber-bg)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid rgba(245, 158, 11, 0.25)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', fontWeight: 600, color: 'var(--accent-amber)', marginBottom: '4px' }}>
                      <AlertCircle size={14} />
                      <span>Data Resilience Audit:</span>
                    </div>
                    {msg.caveats.map((c, i) => (
                      <div key={i} style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                        {c}
                      </div>
                    ))}
                  </div>
                )}

                {/* Suggested Follow-ups */}
                {msg.suggested_followups && msg.suggested_followups.length > 0 && (
                  <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid var(--border-color-subtle)' }}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: '6px', fontWeight: 500 }}>
                      Suggested Follow-up Queries:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {msg.suggested_followups.map((f, i) => (
                        <button
                          key={i}
                          id={`followup-${idx}-${i}`}
                          className="btn btn-chip"
                          onClick={() => handleSendQuery(f)}
                          style={{ fontSize: '0.75rem' }}
                        >
                          {f}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="panel fade-in" style={{ padding: '12px 18px', width: 'fit-content', fontSize: '0.825rem', color: 'var(--accent-cyan)' }}>
            Processing query metrics...
          </div>
        )}
      </div>

      {/* Input Box */}
      <div className="panel" style={{ padding: '10px', display: 'flex', gap: '10px', alignItems: 'center' }}>
        <input
          id="input-chat-query"
          type="text"
          value={queryInput}
          onChange={(e) => setQueryInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendQuery()}
          placeholder="Ask any executive query (e.g. 'How is Mining pipeline looking?', 'What is unbilled backlog?')..."
          style={{
            flex: 1,
            padding: '10px 14px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-color)',
            background: 'var(--bg-app)',
            color: 'var(--text-main)',
            fontSize: '0.88rem',
            outline: 'none'
          }}
        />
        <button
          id="btn-send-query"
          className="btn btn-primary"
          onClick={() => handleSendQuery()}
          disabled={loading}
          style={{ padding: '10px 18px' }}
        >
          <span>Send</span>
          <CornerDownLeft size={14} />
        </button>
      </div>
    </div>
  );
}
