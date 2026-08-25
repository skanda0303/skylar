import React from 'react';
import { TrendingUp, FileText, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function MetricsOverview({ metrics }) {
  const cards = [
    {
      id: 'metric-deals-pipeline',
      title: 'Deals Pipeline',
      value: metrics ? `₹${(metrics.total_deals_pipeline / 1e7).toFixed(2)} Cr` : '₹230.55 Cr',
      description: '345 active deals across sectors',
      badge: 'Pipeline',
      badgeClass: 'badge-cyan',
      panelClass: 'panel-accent-cyan',
      icon: TrendingUp,
      iconColor: 'var(--accent-cyan)'
    },
    {
      id: 'metric-contract-value',
      title: 'Work Orders Value',
      value: metrics ? `₹${(metrics.total_contract_val / 1e7).toFixed(2)} Cr` : '₹21.16 Cr',
      description: '176 active executed projects',
      badge: 'Contracts',
      badgeClass: 'badge-blue',
      panelClass: 'panel-accent-blue',
      icon: FileText,
      iconColor: 'var(--accent-blue)'
    },
    {
      id: 'metric-billed-revenue',
      title: 'Billed Revenue',
      value: metrics ? `₹${(metrics.total_billed / 1e7).toFixed(2)} Cr` : '₹10.74 Cr',
      description: '50.7% billing execution rate',
      badge: 'Billed',
      badgeClass: 'badge-emerald',
      panelClass: 'panel-accent-emerald',
      icon: CheckCircle2,
      iconColor: 'var(--accent-emerald)'
    },
    {
      id: 'metric-operational-risks',
      title: 'Operational Risks',
      value: metrics ? `${metrics.stuck_count} Stuck WOs` : '12 Stuck WOs',
      description: 'Pending KAM escalation',
      badge: 'Attention Needed',
      badgeClass: 'badge-amber',
      panelClass: 'panel-accent-amber',
      icon: AlertTriangle,
      iconColor: 'var(--accent-amber)'
    }
  ];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
      gap: '14px',
      marginBottom: '24px'
    }}>
      {cards.map(card => {
        const Icon = card.icon;
        return (
          <div key={card.id} id={card.id} className={`panel ${card.panelClass}`} style={{ padding: '18px 20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                {card.title}
              </span>
              <span className={`badge ${card.badgeClass}`}>
                {card.badge}
              </span>
            </div>
            <div className="tabular-nums" style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '4px', letterSpacing: '-0.02em' }}>
              {card.value}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {card.description}
            </div>
          </div>
        );
      })}
    </div>
  );
}
