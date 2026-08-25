import React, { useState } from 'react';
import { Sliders, MessageSquare, BarChart2, Database, X, Zap } from 'lucide-react';

export default function Header({ config, setConfig, activeTab, setActiveTab }) {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '14px 32px',
      borderBottom: '1px solid var(--border-color-subtle)',
      background: 'rgba(16, 20, 31, 0.95)',
      backdropFilter: 'blur(12px)',
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      {/* Brand Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: 'var(--radius-md)',
          background: 'var(--accent-cyan-bg)',
          border: '1px solid rgba(56, 189, 248, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Zap size={18} color="var(--accent-cyan)" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            Skylark <span style={{ color: 'var(--accent-cyan)' }}>BI</span>
          </h1>
          <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0 }}>
            Monday.com Business Intelligence Platform
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ display: 'flex', gap: '4px', background: 'var(--bg-app)', padding: '4px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color-subtle)' }}>
        {[
          { id: 'chat', label: 'BI Assistant', icon: MessageSquare },
          { id: 'leadership', label: 'Executive Reports', icon: BarChart2 },
          { id: 'data', label: 'Board Data', icon: Database },
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              className={`btn ${isActive ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '7px 16px',
                fontSize: '0.825rem',
                cursor: 'pointer'
              }}
            >
              <Icon size={14} color={isActive ? '#fff' : 'var(--text-muted)'} />
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
          style={{ fontSize: '0.8rem' }}
        >
          <Sliders size={14} color="var(--accent-cyan)" />
          <span>Monday.com Integration</span>
        </button>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100
        }}>
          <div className="panel fade-in" style={{ width: '440px', padding: '24px', background: 'var(--bg-surface)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>Monday.com Integration Credentials</h3>
              <button className="btn btn-ghost" onClick={() => setShowSettings(false)} style={{ padding: '4px' }}>
                <X size={16} />
              </button>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
              Connect directly to Monday.com GraphQL API v2 or run using local Resilience Engine mirror.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Monday.com API Token
                </label>
                <input
                  id="setting-api-token"
                  type="password"
                  value={config.apiToken}
                  onChange={(e) => setConfig({ ...config, apiToken: e.target.value })}
                  placeholder="Paste Monday.com API Token..."
                  style={{
                    width: '100%',
                    padding: '9px 12px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color)',
                    background: 'var(--bg-app)',
                    color: 'var(--text-main)',
                    fontSize: '0.85rem',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
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
                    padding: '9px 12px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color)',
                    background: 'var(--bg-app)',
                    color: 'var(--text-main)',
                    fontSize: '0.85rem',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
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
                    padding: '9px 12px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color)',
                    background: 'var(--bg-app)',
                    color: 'var(--text-main)',
                    fontSize: '0.85rem',
                    outline: 'none'
                  }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
              <button className="btn btn-primary" onClick={() => setShowSettings(false)}>
                Save Credentials
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
