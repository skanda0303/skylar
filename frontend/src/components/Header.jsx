import React, { useState } from 'react';
import { Sliders, MessageSquare, BarChart2, Database, X } from 'lucide-react';

export default function Header({ config, setConfig, activeTab, setActiveTab }) {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '14px 28px',
      borderBottom: '1px solid var(--border-color-subtle)',
      background: 'var(--bg-surface)'
    }}>
      {/* Brand Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <h1 style={{ fontSize: '1.05rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>
          Skylark <span style={{ color: 'var(--text-dim)', fontWeight: 400 }}>BI</span>
        </h1>
        <span style={{ height: '12px', width: '1px', background: 'var(--border-color)' }} />
        <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Monday.com Intelligence Workspace</span>
      </div>

      {/* Navigation */}
      <nav style={{ display: 'flex', gap: '2px', background: 'var(--bg-app)', padding: '3px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color-subtle)' }}>
        {[
          { id: 'chat', label: 'Assistant', icon: MessageSquare },
          { id: 'leadership', label: 'Executive Reports', icon: BarChart2 },
          { id: 'data', label: 'Board Data', icon: Database },
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              className={`btn ${isActive ? 'btn-secondary' : 'btn-ghost'}`}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '6px 14px',
                fontSize: '0.8rem',
                color: isActive ? 'var(--text-main)' : 'var(--text-muted)',
                cursor: 'pointer'
              }}
            >
              <Icon size={14} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Settings Action */}
      <div>
        <button
          id="btn-open-settings"
          className="btn btn-secondary"
          onClick={() => setShowSettings(true)}
          style={{ fontSize: '0.78rem' }}
        >
          <Sliders size={13} />
          <span>Monday.com Integration</span>
        </button>
      </div>

      {/* Clean Settings Modal */}
      {showSettings && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100
        }}>
          <div className="panel fade-in" style={{ width: '420px', padding: '24px', background: 'var(--bg-surface)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Monday.com Credentials</h3>
              <button className="btn btn-ghost" onClick={() => setShowSettings(false)} style={{ padding: '4px' }}>
                <X size={16} />
              </button>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
              Enter your Monday.com API credentials below. If left blank, the application operates using the dataset mirror.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>
                  API Token
                </label>
                <input
                  id="setting-api-token"
                  type="password"
                  value={config.apiToken}
                  onChange={(e) => setConfig({ ...config, apiToken: e.target.value })}
                  placeholder="Paste API token..."
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color-subtle)',
                    background: 'var(--bg-app)',
                    color: 'var(--text-main)',
                    fontSize: '0.825rem',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>
                  Deals Board ID
                </label>
                <input
                  id="setting-deals-id"
                  type="text"
                  value={config.dealsBoardId}
                  onChange={(e) => setConfig({ ...config, dealsBoardId: e.target.value })}
                  placeholder="e.g. 12345678"
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color-subtle)',
                    background: 'var(--bg-app)',
                    color: 'var(--text-main)',
                    fontSize: '0.825rem',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>
                  Work Orders Board ID
                </label>
                <input
                  id="setting-wo-id"
                  type="text"
                  value={config.woBoardId}
                  onChange={(e) => setConfig({ ...config, woBoardId: e.target.value })}
                  placeholder="e.g. 87654321"
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color-subtle)',
                    background: 'var(--bg-app)',
                    color: 'var(--text-main)',
                    fontSize: '0.825rem',
                    outline: 'none'
                  }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
              <button className="btn btn-primary" onClick={() => setShowSettings(false)}>
                Save Settings
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
