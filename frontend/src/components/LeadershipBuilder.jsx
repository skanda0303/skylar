import React, { useState, useEffect } from 'react';
import { Copy, Check } from 'lucide-react';

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
      <div className="panel" style={{ padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, margin: 0 }}>Executive Leadership Update</h3>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)', margin: 0 }}>
            Generate structured updates for leadership briefings and status reports.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <select
            id="select-sector"
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            style={{
              padding: '6px 12px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-color-subtle)',
              background: 'var(--bg-app)',
              color: 'var(--text-main)',
              fontSize: '0.8rem',
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
            <span>{copied ? 'Copied' : 'Copy Brief'}</span>
          </button>
        </div>
      </div>

      {/* Summary Stat Cards */}
      {reportData && reportData.summary_cards && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '10px' }}>
          {reportData.summary_cards.map((c, i) => (
            <div key={i} className="panel" style={{ padding: '12px 14px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: '2px' }}>{c.title}</div>
              <div className="tabular-nums" style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--text-main)' }}>{c.value}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{c.subtext}</div>
            </div>
          ))}
        </div>
      )}

      {/* Rendered Brief */}
      <div className="panel" style={{ padding: '20px' }}>
        {loading ? (
          <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.8rem' }}>
            Compiling report...
          </div>
        ) : reportData ? (
          <pre style={{
            fontFamily: 'var(--font-family)',
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            color: 'var(--text-main)',
            lineHeight: 1.6,
            fontSize: '0.85rem'
          }}>
            {reportData.markdown_content}
          </pre>
        ) : null}
      </div>
    </div>
  );
}
