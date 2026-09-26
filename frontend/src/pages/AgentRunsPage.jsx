import React, { useState, useEffect } from 'react';
import { History, RefreshCw, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { fetchAgentRuns } from '../api';

export default function AgentRunsPage() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchAgentRuns(50);
      setRuns(res.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="panel-card">
      <div className="panel-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ padding: '8px', background: 'rgba(99, 102, 241, 0.15)', borderRadius: '8px', color: '#a5b4fc' }}>
            <History size={22} />
          </div>
          <div>
            <h2>Agent Execution Logs</h2>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
              Audit trail of every agent run, customers evaluated, duplicate counts, and delivery metrics.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn-secondary" onClick={loadData} title="Refresh execution logs">
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>Run ID</th>
              <th>Started At</th>
              <th>Checked</th>
              <th>Active</th>
              <th>Suspended</th>
              <th>Sent/Simulated</th>
              <th>Skipped (Dups)</th>
              <th>Failed</th>
              <th>Run Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  Loading agent execution history...
                </td>
              </tr>
            ) : runs.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  No previous runs recorded. Click <strong>"RUN AGENT"</strong> in the top header to execute an evaluation cycle.
                </td>
              </tr>
            ) : (
              runs.map((r) => {
                const isSuccess = r.run_status === 'COMPLETED';
                const hasErrors = r.run_status === 'COMPLETED_WITH_ERRORS';
                return (
                  <tr key={r.run_id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                      {r.run_id}
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {new Date(r.started_at).toLocaleString()}
                    </td>
                    <td>{r.customers_checked}</td>
                    <td style={{ color: '#34d399' }}>{r.active_customers}</td>
                    <td style={{ color: '#fb7185' }}>{r.suspended_customers}</td>
                    <td style={{ color: '#38bdf8', fontWeight: 600 }}>{r.notifications_sent}</td>
                    <td style={{ color: '#fbbf24' }}>{r.notifications_skipped}</td>
                    <td style={{ color: r.notifications_failed > 0 ? '#f87171' : 'var(--text-muted)' }}>
                      {r.notifications_failed}
                    </td>
                    <td>
                      <span 
                        className={`status-badge ${
                          isSuccess ? 'badge-sent' : hasErrors ? 'badge-skipped' : 'badge-failed'
                        }`}
                      >
                        {r.run_status}
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
