import React, { useState, useEffect } from 'react';
import { Search, Filter, Edit3, Eye, RefreshCw, Mail, Phone } from 'lucide-react';
import { fetchCustomers, updateCustomerStatus, testCustomerNotification } from '../api';
import EditCustomerModal from '../components/EditCustomerModal';
import TestNotificationModal from '../components/TestNotificationModal';

export default function CustomersPage({ onStatsUpdated }) {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [testResult, setTestResult] = useState(null);
  const [total, setTotal] = useState(0);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchCustomers({
        status: statusFilter,
        search: search,
        limit: 100,
      });
      setCustomers(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadData();
  };

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
        <div>
          <h2>Customer Accounts Directory</h2>
          <div className="panel-subtitle">
            Monitored subscriber service records ({total} total).
          </div>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn-secondary" onClick={loadData} title="Refresh Accounts List">
            <RefreshCw size={13} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="filter-bar">
        <form onSubmit={handleSearchSubmit} className="search-input-wrap">
          <Search size={14} />
          <input
            type="text"
            className="form-input"
            placeholder="Search by customer name, landline, or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </form>

        <div className="filter-pills">
          <button
            className={`filter-pill ${statusFilter === '' ? 'active' : ''}`}
            onClick={() => setStatusFilter('')}
          >
            All Accounts
          </button>
          <button
            className={`filter-pill ${statusFilter === 'Active' ? 'active' : ''}`}
            onClick={() => setStatusFilter('Active')}
          >
            Active Only
          </button>
          <button
            className={`filter-pill ${statusFilter === 'Suspended' ? 'active' : ''}`}
            onClick={() => setStatusFilter('Suspended')}
          >
            Suspended Only
          </button>
        </div>
      </div>

      {/* Customers Table */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
          <RefreshCw size={22} className="spin-anim" style={{ margin: '0 auto 8px auto' }} />
          <div>Loading accounts...</div>
        </div>
      ) : customers.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '48px 20px', color: 'var(--text-muted)' }}>
          {!search && !statusFilter && total === 0 ? (
            <>
              <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '6px' }}>
                No Customer Dataset Loaded
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Please use <strong>"Upload New CSV"</strong> in the left sidebar to import customer records.
              </div>
            </>
          ) : (
            <div>No customer records found matching query.</div>
          )}
        </div>
      ) : (
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Account / Landline</th>
                <th>Subscriber Name</th>
                <th>Status</th>
                <th>Remark / Reason</th>
                <th>Email Address</th>
                <th>Notification State</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((c) => {
                const isSuspended = (c.status || '').toLowerCase() === 'suspended';
                const notifStatus = c.notification_status || 'NONE';

                return (
                  <tr key={c.land_number}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                      {c.land_number}
                    </td>
                    <td style={{ fontWeight: 500 }}>{c.customer_name}</td>
                    <td>
                      <span className={`status-badge ${isSuspended ? 'badge-suspended' : 'badge-active'}`}>
                        <span style={{ fontSize: '0.65rem' }}>●</span>
                        <span>{c.status}</span>
                      </span>
                    </td>
                    <td>
                      <span style={{ color: isSuspended ? '#EF4444' : 'var(--text-secondary)' }}>
                        {c.remark || '—'}
                      </span>
                    </td>
                    <td style={{ color: c.email ? 'var(--text-secondary)' : 'var(--text-muted)', fontSize: '0.82rem' }}>
                      {c.email || '—'}
                    </td>
                    <td>
                      {notifStatus === 'NONE' ? (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.76rem' }}>None</span>
                      ) : (
                        <span className={`status-badge badge-${notifStatus.toLowerCase()}`}>
                          {notifStatus}
                        </span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <div style={{ display: 'inline-flex', gap: '6px' }}>
                        <button
                          className="btn-secondary"
                          onClick={() => setEditingCustomer(c)}
                          style={{ padding: '4px 9px', fontSize: '0.76rem' }}
                          title="Edit Status or Contact Details"
                        >
                          <Edit3 size={12} />
                          <span>Edit</span>
                        </button>
                        <button
                          className="btn-secondary"
                          onClick={() => handleTestNotification(c.land_number)}
                          style={{ padding: '4px 9px', fontSize: '0.76rem' }}
                          title="Evaluate notification logic"
                        >
                          <Eye size={12} />
                          <span>Inspect</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Edit Customer Modal */}
      {editingCustomer && (
        <EditCustomerModal
          customer={editingCustomer}
          onClose={() => setEditingCustomer(null)}
          onSave={handleSaveCustomer}
        />
      )}

      {/* Test / Preview Notification Modal */}
      {testResult && (
        <TestNotificationModal
          result={testResult}
          onClose={() => setTestResult(null)}
        />
      )}
    </div>
  );
}
