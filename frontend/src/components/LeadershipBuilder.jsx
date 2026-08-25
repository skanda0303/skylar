import React, { useState, useEffect } from 'react';
import { Copy, Check, FileText } from 'lucide-react';

export default function LeadershipBuilder({ config }) {
  const [selectedSector, setSelectedSector] = useState('All');
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const fetchLeadershipReport = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/leadership-update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sector: selectedSector,
          report_type: 'executive',
          api_token: config.apiToken,
          deals_board_id: config.dealsBoardId,
          wo_board_id: config.woBoardId
        })
      });
      const data = await res.json();
      setReportData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeadershipReport();
  }, [selectedSector]);

  const copyToClipboard = () => {
    if (reportData && reportData.markdown_content) {
      navigator.clipboard.writeText(reportData.markdown_content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Controls */}
      <div className="panel" style={{ padding: '18px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
            Executive Leadership Brief Generator
          </h3>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>
            Real-time executive summaries compiled from Monday.com boards. Copy directly to Slack, Email, or Board Slides.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <select
            id="select-sector"
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            style={{
              padding: '8px 14px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)',
              background: 'var(--bg-app)',
              color: 'var(--text-main)',
              fontSize: '0.825rem',
              outline: 'none'
            }}
          >
            <option value="All">All Sectors</option>
            <option value="Mining">Mining</option>
            <option value="Powerline">Powerline</option>
            <option value="Renewables">Renewables</option>
            <option value="Railways">Railways</option>
            <option value="Construction">Construction</option>
            <option value="DSP">DSP</option>
          </select>

          <button
            id="btn-copy-brief"
            className="btn btn-primary"
            onClick={copyToClipboard}
          >
            {copied ? <Check size={14} /> : <Copy size={14} />}
            <span>{copied ? 'Copied to Clipboard!' : 'Copy Executive Brief'}</span>
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {reportData && reportData.summary_cards && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
          {reportData.summary_cards.map((c, i) => (
            <div key={i} className="panel" style={{ padding: '14px 16px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>{c.title}</div>
              <div className="tabular-nums" style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '2px' }}>{c.value}</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--accent-cyan)' }}>{c.subtext}</div>
            </div>
          ))}
        </div>
      )}

      {/* Rendered Brief */}
      <div className="panel" style={{ padding: '24px' }}>
        {loading ? (
          <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            Compiling executive report...
          </div>
        ) : reportData ? (
          <pre style={{
            fontFamily: 'var(--font-family)',
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            color: 'var(--text-main)',
            lineHeight: 1.6,
            fontSize: '0.88rem'
          }}>
            {reportData.markdown_content}
          </pre>
        ) : null}
      </div>
    </div>
  );
}
