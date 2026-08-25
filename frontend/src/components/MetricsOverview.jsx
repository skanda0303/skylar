import React from 'react';

export default function MetricsOverview({ metrics }) {
  const cards = [
    {
      id: 'metric-deals-pipeline',
      title: 'Deals Pipeline',
      value: metrics ? `₹${(metrics.total_deals_pipeline / 1e5).toFixed(1)}L` : '₹2,482.5L',
      description: '345 active deals across sectors'
    },
    {
      id: 'metric-contract-value',
      title: 'Work Orders Value',
      value: metrics ? `₹${(metrics.total_contract_val / 1e5).toFixed(1)}L` : '₹1,180.4L',
      description: '176 active execution projects'
    },
    {
      id: 'metric-billed-revenue',
      title: 'Billed Revenue',
      value: metrics ? `₹${(metrics.total_billed / 1e5).toFixed(1)}L` : '₹895.2L',
      description: '75.8% contract billing progress'
    },
    {
      id: 'metric-operational-risks',
      title: 'Stuck Work Orders',
      value: metrics ? `${metrics.stuck_count}` : '12',
      description: 'Projects pending escalation'
    }
  ];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
      gap: '12px',
      marginBottom: '20px'
    }}>
      {cards.map(card => (
        <div key={card.id} id={card.id} className="panel" style={{ padding: '16px 20px' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginBottom: '6px', fontWeight: 500 }}>
            {card.title}
          </div>
          <div className="tabular-nums" style={{ fontSize: '1.45rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px', letterSpacing: '-0.02em' }}>
            {card.value}
          </div>
          <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
            {card.description}
          </div>
        </div>
      ))}
    </div>
  );
}
