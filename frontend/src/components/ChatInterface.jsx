import React, { useState } from 'react';
import { Send, CornerDownLeft } from 'lucide-react';

export default function ChatInterface({ config }) {
  const [queryInput, setQueryInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: 'agent',
      headline: 'Business Intelligence Assistant',
      summary_insights: [
        'Query business performance across Work Orders and Deals boards.',
        'Data resilience engine handles missing deal values, sector normalization, and probability-weighted pipeline calculation.'
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
        summary_insights: ['Failed to connect to backend server.'],
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
        marginTop: '14px',
        padding: '14px',
        background: 'var(--bg-app)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-color-subtle)'
      }}>
        <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '10px' }}>
          {chart.title}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {chart.labels.map((label, idx) => {
            const val = chart.values[idx] || 0;
            const pct = Math.min(100, Math.max(5, (val / maxVal) * 100));
            return (
              <div key={idx} style={{ fontSize: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px', color: 'var(--text-muted)' }}>
                  <span>{label}</span>
                  <span className="tabular-nums" style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                    {typeof val === 'number' ? (val > 1000 ? `₹${val.toLocaleString()}` : val) : val}
                  </span>
                </div>
                <div style={{ width: '100%', height: '4px', background: 'var(--bg-surface-subtle)', borderRadius: '2px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${pct}%`,
                    height: '100%',
                    background: 'var(--accent-primary)',
                    borderRadius: '2px',
                    transition: 'width 0.3s ease'
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
      {/* Sample Query Chips */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
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
            {prompt}
          </button>
        ))}
      </div>

      {/* Message Stream */}
      <div style={{
        minHeight: '360px',
        maxHeight: '520px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
        paddingRight: '2px'
      }}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className="fade-in"
            style={{
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: msg.sender === 'user' ? '70%' : '100%',
              width: msg.sender === 'agent' ? '100%' : 'auto'
            }}
          >
            {msg.sender === 'user' ? (
              <div style={{
                background: 'var(--bg-surface-subtle)',
                border: '1px solid var(--border-color-subtle)',
                color: 'var(--text-main)',
                padding: '8px 14px',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.85rem'
              }}>
                {msg.text}
              </div>
            ) : (
              <div className="panel" style={{ padding: '18px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>{msg.headline || 'Summary'}</h4>
                  {msg.data_source && (
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{msg.data_source}</span>
                  )}
                </div>

                {/* Summary Insights */}
                {msg.summary_insights && msg.summary_insights.length > 0 && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
                    {msg.summary_insights.map((insight, i) => {
                      const parts = insight.split(/(\*\*.*?\*\*)/g);
                      return (
                        <div key={i} style={{ fontSize: '0.825rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                          {parts.map((p, pIdx) => {
                            if (p.startsWith('**') && p.endsWith('**')) {
                              return <strong key={pIdx} style={{ color: 'var(--text-main)', fontWeight: 600 }}>{p.slice(2, -2)}</strong>;
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

                {/* Resilience Caveats Box */}
                {msg.caveats && msg.caveats.length > 0 && (
                  <div style={{
                    marginTop: '12px',
                    padding: '8px 12px',
                    background: 'var(--bg-app)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color-subtle)'
                  }}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontWeight: 500, marginBottom: '2px' }}>
                      Data Quality Notes:
                    </div>
                    {msg.caveats.map((c, i) => (
                      <div key={i} style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                        {c}
                      </div>
                    ))}
                  </div>
                )}

                {/* Follow-up Buttons */}
                {msg.suggested_followups && msg.suggested_followups.length > 0 && (
                  <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid var(--border-color-subtle)' }}>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {msg.suggested_followups.map((f, i) => (
                        <button
                          key={i}
                          id={`followup-${idx}-${i}`}
                          className="btn btn-chip"
                          onClick={() => handleSendQuery(f)}
                          style={{ fontSize: '0.74rem' }}
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
          <div className="panel fade-in" style={{ padding: '10px 16px', width: 'fit-content', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
            Processing query...
          </div>
        )}
      </div>

      {/* Input Box */}
      <div className="panel" style={{ padding: '8px', display: 'flex', gap: '8px', alignItems: 'center' }}>
        <input
          id="input-chat-query"
          type="text"
          value={queryInput}
          onChange={(e) => setQueryInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendQuery()}
          placeholder="Ask a question about sales pipeline, revenue, or work orders..."
          style={{
            flex: 1,
            padding: '8px 12px',
            borderRadius: 'var(--radius-sm)',
            border: 'none',
            background: 'transparent',
            color: 'var(--text-main)',
            fontSize: '0.85rem',
            outline: 'none'
          }}
        />
        <button
          id="btn-send-query"
          className="btn btn-primary"
          onClick={() => handleSendQuery()}
          disabled={loading}
          style={{ padding: '7px 12px' }}
        >
          <span>Send</span>
          <CornerDownLeft size={13} />
        </button>
      </div>
    </div>
  );
}
