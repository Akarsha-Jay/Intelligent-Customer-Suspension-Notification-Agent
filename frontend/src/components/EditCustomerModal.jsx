import React, { useState, useEffect } from 'react';
import { X, Save, Edit3, AlertCircle } from 'lucide-react';

const COMMON_REMARKS = [
  'Bill overdue',
  'Payment not received',
  'Customer requested temporary suspension',
  'Technical issue',
  'Account issue',
  'Verification required',
  'Account active',
  'In good standing',
];

export default function EditCustomerModal({ customer, onClose, onSave }) {
  const [status, setStatus] = useState(customer?.status || 'Active');
  const [remark, setRemark] = useState(customer?.remark || '');
  const [email, setEmail] = useState(customer?.email || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!customer) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await onSave(customer.land_number, {
        status,
        remark,
        email,
      });
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to save changes');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Edit Subscriber Account</h3>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              {customer.customer_name} • {customer.land_number}
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && (
              <div
                style={{
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(239, 68, 68, 0.12)',
                  color: '#f87171',
                  border: '1px solid rgba(239, 68, 68, 0.25)',
                  marginBottom: '16px',
                  fontSize: '0.82rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <AlertCircle size={15} />
                <span>{error}</span>
              </div>
            )}

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Service Status
              </label>
              <select
                style={{
                  width: '100%',
                  background: 'var(--bg-input)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text-primary)',
                  padding: '8px 12px',
                  fontSize: '0.85rem',
                  outline: 'none',
                }}
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                id="edit-status-select"
              >
                <option value="Active">Active (Normal Service)</option>
                <option value="Suspended">Suspended (Service Disconnected)</option>
              </select>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Operational Remark / Suspension Reason
              </label>
              <input
                type="text"
                className="form-input"
                style={{ paddingLeft: '12px' }}
                value={remark}
                onChange={(e) => setRemark(e.target.value)}
                placeholder="e.g. Bill overdue, Payment not received..."
                id="edit-remark-input"
              />
              <div style={{ marginTop: '8px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Quick templates:</span>
                {COMMON_REMARKS.slice(0, 4).map((r) => (
                  <button
                    key={r}
                    type="button"
                    style={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-secondary)',
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-xs)',
                      fontSize: '0.72rem',
                      cursor: 'pointer',
                    }}
                    onClick={() => setRemark(r)}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Contact Email Address
              </label>
              <input
                type="email"
                className="form-input"
                style={{ paddingLeft: '12px' }}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="subscriber@example.com"
                id="edit-email-input"
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              <Save size={14} />
              <span>{saving ? 'Saving...' : 'Save Changes'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
