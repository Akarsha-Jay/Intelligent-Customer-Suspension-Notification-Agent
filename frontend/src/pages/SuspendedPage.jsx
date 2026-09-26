import React, { useState, useEffect } from 'react';
import { UserX, RefreshCw, Sparkles, Edit3 } from 'lucide-react';
import { fetchSuspendedCustomers, updateCustomerStatus, testCustomerNotification } from '../api';
import EditCustomerModal from '../components/EditCustomerModal';
import TestNotificationModal from '../components/TestNotificationModal';

export default function SuspendedPage({ onStatsUpdated }) {
  const [suspended, setSuspended] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [testResult, setTestResult] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchSuspendedCustomers();
      setSuspended(res.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSaveCustomer = async (landNumber, updateData) => {
    await updateCustomerStatus(landNumber, updateData);
    await loadData();
    if (onStatsUpdated) onStatsUpdated();
  };

  const handleTestNotification = async (landNumber) => {
    try {
      const res = await testCustomerNotification(landNumber);
      setTestResult(res);
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="panel-card">
      <div className="panel-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ padding: '8px', background: 'rgba(244, 63, 94, 0.15)', borderRadius: '8px', color: '#fb7185' }}>
            <UserX size={22} />
          </div>
          <div>
            <h2>Suspended Customers Queue</h2>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
              Showing {suspended.length} accounts currently in Suspended state requiring agent review.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn-secondary" onClick={loadData} title="Refresh Suspended Queue">
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
        </div>
      </div>


      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>Landline</th>
              <th>Customer Name</th>
              <th>Email Address</th>
              <th>Suspension Reason</th>
              <th>Notification Status</th>
              <th>Event ID</th>
              <th>Last Notified</th>
              <th style={{ textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  Loading suspended customers...
                </td>
              </tr>
            ) : suspended.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  No customers currently suspended. All accounts active!
                </td>
              </tr>
            ) : (
              suspended.map((c) => (
                <tr key={c.land_number}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                    {c.land_number}
                  </td>
                  <td style={{ fontWeight: 500 }}>{c.customer_name}</td>
                  <td style={{ color: c.email ? 'var(--text-secondary)' : '#f59e0b', fontSize: '0.82rem' }}>
                    {c.email || '(Missing Email)'}
                  </td>
                  <td style={{ color: '#fca5a5', fontWeight: 500 }}>
                    {c.remark || 'Suspended'}
                  </td>
                  <td>
                    <span className={`status-badge badge-${(c.notification_status || 'PENDING').toLowerCase()}`}>
                      {c.notification_status || 'PENDING'}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {c.current_event_id || '—'}
                  </td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    {c.last_notified_at ? new Date(c.last_notified_at).toLocaleString() : 'Never'}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: '6px' }}>
                      <button
                        className="btn-secondary"
                        style={{ padding: '5px 10px', fontSize: '0.78rem' }}
                        onClick={() => setEditingCustomer(c)}
                        title="Edit status or restore to Active"
                      >
                        <Edit3 size={13} />
                        <span>Edit</span>
                      </button>
                      <button
                        className="btn-secondary"
                        style={{ padding: '5px 10px', fontSize: '0.78rem', background: 'rgba(59, 130, 246, 0.12)', color: '#93c5fd' }}
                        onClick={() => handleTestNotification(c.land_number)}
                        title="Evaluate agent decision"
                      >
                        <Sparkles size={13} />
                        <span>Preview</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {editingCustomer && (
        <EditCustomerModal
          customer={editingCustomer}
          onClose={() => setEditingCustomer(null)}
          onSave={handleSaveCustomer}
        />
      )}

      {testResult && (
        <TestNotificationModal
          result={testResult}
          onClose={() => setTestResult(null)}
        />
      )}
    </div>
  );
}
