import React, { useEffect } from 'react';
import { X, Search, CheckCircle, Info, Tag } from 'lucide-react';

export default function TestNotificationModal({ result, onClose }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!result) return null;

  const isSuccess = result.success;
  const isDuplicate = result.action === 'SKIP_DUPLICATE';
  const isSkipActive = result.action === 'SKIP_ACTIVE';
  const isMissingEmail = result.action === 'SKIP_MISSING_EMAIL';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Account Notification Evaluation</h3>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Subscriber: {result.customer?.customer_name} • {result.customer?.land_number}
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {/* Decision Banner */}
          <div
            style={{
              padding: '12px 16px',
              borderRadius: 'var(--radius-md)',
              background: isSuccess && !isDuplicate && !isSkipActive ? 'rgba(16, 185, 129, 0.12)' : 'rgba(245, 158, 11, 0.12)',
              border: `1px solid ${isSuccess && !isDuplicate && !isSkipActive ? 'rgba(16, 185, 129, 0.25)' : 'rgba(245, 158, 11, 0.25)'}`,
              marginBottom: '18px',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
            }}
          >
            {isSuccess && !isDuplicate && !isSkipActive ? (
              <CheckCircle size={18} color="#34d399" style={{ flexShrink: 0, marginTop: '2px' }} />
            ) : (
              <Info size={18} color="#fbbf24" style={{ flexShrink: 0, marginTop: '2px' }} />
            )}
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.88rem', color: isSuccess && !isDuplicate && !isSkipActive ? '#34d399' : '#fbbf24' }}>
                Action: {result.action}
              </div>
              <div style={{ fontSize: '0.82rem', marginTop: '3px', color: 'var(--text-secondary)' }}>
                {result.message || 'Notification evaluation completed.'}
              </div>
            </div>
          </div>

          {/* Analysis Details */}
          {result.analysis && (
            <div style={{ background: 'var(--bg-elevated)', padding: '14px 16px', borderRadius: 'var(--radius-md)', marginBottom: '18px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                Remark Classification
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '0.82rem' }}>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Classified Category: </span>
                  <strong>{result.category}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Confidence Score: </span>
                  <span>{Math.round((result.analysis?.confidence || 1.0) * 100)}%</span>
                </div>
                <div style={{ gridColumn: '1 / -1' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Rule Explanation: </span>
                  <span>{result.analysis?.explanation}</span>
                </div>
              </div>
            </div>
          )}

          {/* Generated Email Preview */}
          {result.email_preview && (
            <div className="email-preview-box">
              <div className="email-headers">
                <div>
                  <strong>Subject:</strong> {result.email_preview.subject}
                </div>
                <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                  Mode: {result.email_preview.generation_mode}
                </div>
              </div>
              <div className="email-body">
                {result.email_preview.body}
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-primary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
