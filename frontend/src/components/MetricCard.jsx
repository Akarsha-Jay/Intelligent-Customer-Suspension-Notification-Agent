import React from 'react';

export default function MetricCard({ title, value, footer, icon: Icon, color = 'blue' }) {
  const colorMap = {
    blue: {
      bg: 'rgba(0, 91, 172, 0.12)',
      color: '#0090D0',
      border: 'rgba(0, 91, 172, 0.3)',
    },
    emerald: {
      bg: 'var(--mobitel-green-tint)',
      color: 'var(--mobitel-green)',
      border: 'var(--mobitel-green-border)',
    },
    rose: {
      bg: 'var(--danger-red-tint)',
      color: '#EF4444',
      border: 'var(--danger-red-border)',
    },
    cyan: {
      bg: 'rgba(0, 144, 208, 0.12)',
      color: 'var(--slt-cyan)',
      border: 'rgba(0, 144, 208, 0.3)',
    },
    amber: {
      bg: 'rgba(245, 158, 11, 0.12)',
      color: '#F59E0B',
      border: 'rgba(245, 158, 11, 0.3)',
    },
  };

  const scheme = colorMap[color] || colorMap.blue;

  return (
    <div className="metric-card">
      <div className="metric-header">
        <span>{title}</span>
        {Icon && (
          <div
            className="metric-icon-wrap"
            style={{
              background: scheme.bg,
              color: scheme.color,
              border: `1px solid ${scheme.border}`,
            }}
          >
            <Icon size={16} />
          </div>
        )}
      </div>
      <div className="metric-value">{value}</div>
      {footer && <div className="metric-footer">{footer}</div>}
    </div>
  );
}
