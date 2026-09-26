import React, { useState, useEffect } from 'react';
import { X, Copy, Check, Mail, MessageSquare, Clock, Hash, Tag, Send } from 'lucide-react';

export default function EmailModal({ notification, onClose }) {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!notification) return null;

  const isWhatsApp = notification.channel === 'WHATSAPP';

  const handleCopy = () => {
    const content = notification.email_content || '';
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(content);
    } else {
      const textArea = document.createElement('textarea');
      textArea.value = content;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const statusClass = notification.delivery_status
    ? `badge-${notification.delivery_status.toLowerCase()}`
    : '';

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ 
              padding: '8px', 
              background: isWhatsApp ? 'rgba(37, 211, 102, 0.15)' : 'rgba(59, 130, 246, 0.15)', 
              borderRadius: '8px', 
              color: isWhatsApp ? '#25D366' : '#60a5fa' 
            }}>
              {isWhatsApp ? <MessageSquare size={20} /> : <Mail size={20} />}
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem' }}>
                {isWhatsApp ? 'WhatsApp Notice Record' : 'Email Dispatch Record'}
              </h3>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                ID: {notification.notification_id}
              </div>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close modal">
            <X size={20} />
          </button>
        </div>

        <div className="email-preview-box">
          <div className="email-headers">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
              <div>
                <strong>To:</strong> {notification.customer_name} &nbsp;
                {isWhatsApp ? (
                  <span style={{ color: '#25D366', fontWeight: 600 }}>
                    {notification.whatsapp_number || '(No WhatsApp phone)'}
                  </span>
                ) : (
                  <span>&lt;{notification.email || '(No email provided)'}&gt;</span>
                )}
              </div>
              <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                <span
                  style={{
                    fontSize: '0.72rem',
                    fontWeight: 600,
                    padding: '2px 8px',
                    borderRadius: '12px',
                    background: isWhatsApp ? 'rgba(37, 211, 102, 0.15)' : 'rgba(56, 189, 248, 0.15)',
                    color: isWhatsApp ? '#25D366' : '#38bdf8',
                  }}
                >
                  {isWhatsApp ? '💬 WhatsApp' : '✉️ Email'}
                </span>
                {notification.delivery_status && (
                  <span className={`status-badge ${statusClass}`}>
                    {notification.delivery_status}
                  </span>
                )}
              </div>
            </div>

            <div>
              <strong>Landline:</strong> <span style={{ fontFamily: 'var(--font-mono)' }}>{notification.land_number}</span>
            </div>

            <div>
              <strong>Subject:</strong> {notification.subject}
            </div>

            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginTop: '6px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Tag size={13} />
                <span>Category: </span>
                <span className="category-chip">{notification.notification_type}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Clock size={13} />
                <span>
                  Timestamp: {notification.created_at ? new Date(notification.created_at).toLocaleString() : 'N/A'}
                </span>
              </div>
              {notification.suspension_event_id && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Hash size={13} />
                  <span>Event ID: {notification.suspension_event_id}</span>
                </div>
              )}
            </div>
          </div>

          <div className="email-body">
            {notification.email_content || '(No email content available)'}
          </div>
        </div>

        <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <button className="btn-secondary" onClick={handleCopy}>
            {copied ? <Check size={16} color="#10b981" /> : <Copy size={16} />}
            <span>{copied ? 'Copied Body' : 'Copy Email Body'}</span>
          </button>
          <button className="btn-primary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
