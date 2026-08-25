import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

export default function DataExplorer() {
  const [activeBoard, setActiveBoard] = useState('deals');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetch('/api/boards')
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="panel" style={{ padding: '20px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.8rem' }}>Loading board records...</div>;
  }

  const rows = activeBoard === 'deals' ? (data?.deals || []) : (data?.work_orders || []);
  const filteredRows = rows.filter(r => {
    if (!searchTerm) return true;
    return Object.values(r).some(val => String(val).toLowerCase().includes(searchTerm.toLowerCase()));
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      {/* Controls */}
      <div className="panel" style={{ padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', gap: '6px' }}>
          <button
            id="btn-board-deals"
            className={`btn ${activeBoard === 'deals' ? 'btn-secondary' : 'btn-ghost'}`}
            onClick={() => setActiveBoard('deals')}
            style={{ fontSize: '0.8rem' }}
          >
            Deals ({data?.deals_count} records)
          </button>

          <button
            id="btn-board-wo"
            className={`btn ${activeBoard === 'work_orders' ? 'btn-secondary' : 'btn-ghost'}`}
            onClick={() => setActiveBoard('work_orders')}
            style={{ fontSize: '0.8rem' }}
          >
            Work Orders ({data?.wo_count} records)
          </button>
        </div>

        {/* Filter Input */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'var(--bg-app)', padding: '5px 10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color-subtle)' }}>
          <Search size={13} color="var(--text-dim)" />
          <input
            id="input-search-board"
            type="text"
            placeholder="Search records..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-main)', fontSize: '0.8rem', outline: 'none', width: '160px' }}
          />
        </div>
      </div>

      {/* Dataset Table */}
      <div className="panel" style={{ overflowX: 'auto', padding: 0 }}>
        <table className="clean-table">
          <thead>
            {activeBoard === 'deals' ? (
              <tr>
                <th>Deal Name</th>
                <th>Sector</th>
                <th>Value (₹)</th>
                <th>Probability</th>
                <th>Weighted (₹)</th>
                <th>Stage</th>
                <th>Owner</th>
                <th>Client</th>
              </tr>
            ) : (
              <tr>
                <th>Deal Name</th>
                <th>Customer</th>
                <th>Sector</th>
                <th>PO Amount (₹)</th>
                <th>Billed (₹)</th>
                <th>Billing Status</th>
                <th>Execution</th>
                <th>Owner</th>
              </tr>
            )}
          </thead>
          <tbody>
            {filteredRows.slice(0, 50).map((row, idx) => (
              <tr key={idx}>
                {activeBoard === 'deals' ? (
                  <>
                    <td style={{ fontWeight: 500 }}>{row.deal_name}</td>
                    <td><span className="badge badge-neutral">{row.sector}</span></td>
                    <td className="tabular-nums">₹{Number(row.deal_value || 0).toLocaleString()}</td>
                    <td className="tabular-nums">{Math.round((row.closure_probability || 0) * 100)}%</td>
                    <td className="tabular-nums">₹{Number(row.weighted_deal_value || 0).toLocaleString()}</td>
                    <td><span className="badge badge-neutral">{row.deal_stage}</span></td>
                    <td>{row.owner_code}</td>
                    <td>{row.client_code}</td>
                  </>
                ) : (
                  <>
                    <td style={{ fontWeight: 500 }}>{row.deal_name}</td>
                    <td>{row.customer_code}</td>
                    <td><span className="badge badge-neutral">{row.sector}</span></td>
                    <td className="tabular-nums">₹{Number(row.amount_excl_gst || 0).toLocaleString()}</td>
                    <td className="tabular-nums">₹{Number(row.billed_excl_gst || 0).toLocaleString()}</td>
                    <td>
                      <span className={`badge ${row.billing_status === 'Billed' ? 'badge-success' : row.billing_status === 'Stuck' ? 'badge-warning' : 'badge-neutral'}`}>
                        {row.billing_status}
                      </span>
                    </td>
                    <td>{row.execution_status}</td>
                    <td>{row.owner_code}</td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
