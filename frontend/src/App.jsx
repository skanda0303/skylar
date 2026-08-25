import React, { useState } from 'react';
import Header from './components/Header';
import MetricsOverview from './components/MetricsOverview';
import ChatInterface from './components/ChatInterface';
import LeadershipBuilder from './components/LeadershipBuilder';
import DataExplorer from './components/DataExplorer';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [config, setConfig] = useState({
    apiToken: '',
    dealsBoardId: '',
    woBoardId: ''
  });

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-app)' }}>
      <Header
        config={config}
        setConfig={setConfig}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <main style={{ flex: 1, padding: '24px 32px', maxWidth: '1280px', margin: '0 auto', width: '100%' }}>
        <MetricsOverview />

        {activeTab === 'chat' && <ChatInterface config={config} />}
        {activeTab === 'leadership' && <LeadershipBuilder config={config} />}
        {activeTab === 'data' && <DataExplorer config={config} />}
      </main>

      <footer style={{
        padding: '16px 32px',
        borderTop: '1px solid var(--border-color-subtle)',
        textAlign: 'center',
        fontSize: '0.75rem',
        color: 'var(--text-dim)',
        background: 'var(--bg-surface)'
      }}>
        Skylark Drones — Monday.com Business Intelligence Platform
      </footer>
    </div>
  );
}
