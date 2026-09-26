import React, { useState } from 'react';
import { Settings, ShieldCheck, Mail, MessageSquare, Cpu, Database, RefreshCw, Info, RotateCcw, Trash2, Send, CheckCircle2 } from 'lucide-react';
import { toggleEmailMode, toggleWhatsAppMode, updateChannelStrategy, testWhatsApp, clearDataset, clearSystemCache } from '../api';

export default function SettingsPage({ settingsData, onSettingsUpdated, onStatsUpdated }) {
  const [clearingDataset, setClearingDataset] = useState(false);
  const [clearingCache, setClearingCache] = useState(false);
  const [togglingEmail, setTogglingEmail] = useState(false);
  const [togglingWhatsApp, setTogglingWhatsApp] = useState(false);
  const [updatingStrategy, setUpdatingStrategy] = useState(false);
  const [testNumber, setTestNumber] = useState('+94770000001');
  const [testingWhatsApp, setTestingWhatsApp] = useState(false);
  const [msg, setMsg] = useState('');

  const currentStrategy = settingsData?.channel_strategy || 'BOTH';

  const handleSelectStrategy = async (strategy) => {
    setUpdatingStrategy(true);
    try {
      await updateChannelStrategy(strategy);
      if (onSettingsUpdated) onSettingsUpdated();
      const label = strategy === 'EMAIL_ONLY' ? 'Email Only' : strategy === 'WHATSAPP_ONLY' ? 'WhatsApp Only' : 'Both Channels (Omnichannel)';
      setMsg(`Active notification dispatch channel updated to: ${label}`);
      setTimeout(() => setMsg(''), 3500);
    } catch (err) {
      alert(err.message);
    } finally {
      setUpdatingStrategy(false);
    }
  };

  const handleToggleEmail = async () => {
    setTogglingEmail(true);
    try {
      await toggleEmailMode();
      if (onSettingsUpdated) onSettingsUpdated();
      setMsg('Email delivery mode toggled successfully.');
      setTimeout(() => setMsg(''), 3000);
    } catch (err) {
      alert(err.message);
    } finally {
      setTogglingEmail(false);
    }
  };

  const handleToggleWhatsApp = async () => {
    setTogglingWhatsApp(true);
    try {
      await toggleWhatsAppMode();
      if (onSettingsUpdated) onSettingsUpdated();
      setMsg('WhatsApp delivery mode toggled successfully.');
      setTimeout(() => setMsg(''), 3000);
    } catch (err) {
      alert(err.message);
    } finally {
      setTogglingWhatsApp(false);
    }
  };

  const handleTestWhatsApp = async () => {
    if (!testNumber) {
      alert('Please enter a recipient WhatsApp phone number (e.g. +94770000001)');
      return;
    }
    setTestingWhatsApp(true);
    try {
      const res = await testWhatsApp(testNumber);
      if (res.success) {
        setMsg(`WhatsApp test dispatch status: ${res.status}`);
      } else {
        alert(`WhatsApp test failed: ${res.error || 'Unknown error'}`);
      }
      setTimeout(() => setMsg(''), 4000);
    } catch (err) {
      alert(err.message);
    } finally {
      setTestingWhatsApp(false);
    }
  };

  const handleClearDataset = async () => {
    if (!window.confirm('Clear the currently loaded customer dataset? All uploaded records and duplicate prevention history will be cleared.')) {
      return;
    }
    setClearingDataset(true);
    try {
      await clearDataset();
      if (onStatsUpdated) onStatsUpdated();
      setMsg('Dataset and duplicate prevention cache cleared successfully.');
      setTimeout(() => setMsg(''), 3000);
    } catch (err) {
      alert(err.message);
    } finally {
      setClearingDataset(false);
    }
  };

  const handleClearCache = async () => {
    if (!window.confirm('Clear duplicate notification prevention cache? This allows all suspended customer accounts to receive notifications fresh on the next agent run.')) {
      return;
    }
    setClearingCache(true);
    try {
      const res = await clearSystemCache();
      if (onStatsUpdated) onStatsUpdated();
      setMsg(res.message || 'Duplicate prevention cache cleared successfully.');
      setTimeout(() => setMsg(''), 3000);
    } catch (err) {
      alert(err.message);
    } finally {
      setClearingCache(false);
    }
  };

  const isRealSmtp = settingsData?.email_mode === 'REAL_SMTP';
  const isRealWhatsApp = settingsData?.whatsapp_mode === 'REAL_META';

  return (
    <div style={{ maxWidth: '860px', margin: '0 auto' }}>
      <div className="panel-card">
        <div className="panel-header">
          <div>
            <h2>System Configuration & Channels</h2>
            <div className="panel-subtitle">
              Choose active dispatch channel, configure gateways, and manage customer data.
            </div>
          </div>
        </div>

        {msg && (
          <div
            style={{
              padding: '10px 14px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(16, 185, 129, 0.12)',
              color: '#34d399',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              marginBottom: '20px',
              fontSize: '0.85rem',
            }}
          >
            {msg}
          </div>
        )}

        {/* Dispatch Channel Strategy Selector */}
        <div
          style={{
            background: 'var(--bg-elevated)',
            padding: '20px',
            borderRadius: 'var(--radius-md)',
            marginBottom: '20px',
            border: '1px solid var(--border-color)',
          }}
        >
          <div style={{ marginBottom: '14px' }}>
            <h3 style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
              Notification Dispatch Channel Selection
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>
              Choose which communication channel(s) will be sent when the agent runs:
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
            {/* WhatsApp Only Option */}
            <button
              onClick={() => handleSelectStrategy('WHATSAPP_ONLY')}
              disabled={updatingStrategy}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '14px 16px',
                borderRadius: 'var(--radius-md)',
                border: currentStrategy === 'WHATSAPP_ONLY' ? '2px solid #25D366' : '1px solid var(--border-color)',
                background: currentStrategy === 'WHATSAPP_ONLY' ? 'rgba(37, 211, 102, 0.12)' : 'var(--bg-card)',
                color: currentStrategy === 'WHATSAPP_ONLY' ? '#25D366' : 'var(--text-primary)',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
            >
              <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(37, 211, 102, 0.15)', color: '#25D366' }}>
                <MessageSquare size={20} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: '0.88rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span>WhatsApp Only</span>
                  {currentStrategy === 'WHATSAPP_ONLY' && <CheckCircle2 size={16} />}
                </div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>Send solely via WhatsApp</div>
              </div>
            </button>

            {/* Email Only Option */}
            <button
              onClick={() => handleSelectStrategy('EMAIL_ONLY')}
              disabled={updatingStrategy}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '14px 16px',
                borderRadius: 'var(--radius-md)',
                border: currentStrategy === 'EMAIL_ONLY' ? '2px solid #38bdf8' : '1px solid var(--border-color)',
                background: currentStrategy === 'EMAIL_ONLY' ? 'rgba(56, 189, 248, 0.12)' : 'var(--bg-card)',
                color: currentStrategy === 'EMAIL_ONLY' ? '#38bdf8' : 'var(--text-primary)',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
            >
              <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
                <Mail size={20} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: '0.88rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span>Email Only</span>
                  {currentStrategy === 'EMAIL_ONLY' && <CheckCircle2 size={16} />}
                </div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>Send solely via Email</div>
              </div>
            </button>

            {/* Both Channels Option */}
            <button
              onClick={() => handleSelectStrategy('BOTH')}
              disabled={updatingStrategy}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '14px 16px',
                borderRadius: 'var(--radius-md)',
                border: currentStrategy === 'BOTH' ? '2px solid #a855f7' : '1px solid var(--border-color)',
                background: currentStrategy === 'BOTH' ? 'rgba(168, 85, 247, 0.12)' : 'var(--bg-card)',
                color: currentStrategy === 'BOTH' ? '#c084fc' : 'var(--text-primary)',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
            >
              <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' }}>
                <RefreshCw size={20} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: '0.88rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span>Both Channels</span>
                  {currentStrategy === 'BOTH' && <CheckCircle2 size={16} />}
                </div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>Send Email and WhatsApp</div>
              </div>
            </button>
          </div>
        </div>

        {/* Email Mode Card */}
        <div style={{ background: 'var(--bg-elevated)', padding: '18px 20px', borderRadius: 'var(--radius-md)', marginBottom: '16px', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Mail size={18} color="#38bdf8" />
              <div>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Email Notification Gateway</h3>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  Controls whether email alerts are simulated or transmitted via real SMTP.
                </p>
              </div>
            </div>
            <button className="btn-secondary" onClick={handleToggleEmail} disabled={togglingEmail} style={{ fontSize: '0.8rem' }}>
              <span>Switch to {isRealSmtp ? 'Simulation' : 'Live SMTP'}</span>
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', fontSize: '0.82rem' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Active Mode: </span>
              <strong style={{ color: isRealSmtp ? '#34d399' : '#38bdf8' }}>
                {settingsData?.email_mode || 'SIMULATION'}
              </strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>SMTP Host: </span>
              <span>{settingsData?.smtp_host || '(None)'}</span>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Sender Address: </span>
              <span>{settingsData?.sender_email || 'notifications@example.com'}</span>
            </div>
          </div>
        </div>

        {/* WhatsApp Meta Cloud API Card */}
        <div style={{ background: 'var(--bg-elevated)', padding: '18px 20px', borderRadius: 'var(--radius-md)', marginBottom: '16px', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <MessageSquare size={18} color="#25D366" />
              <div>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Meta WhatsApp Cloud API Gateway</h3>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  Official Meta WhatsApp Business Cloud API integration for instant suspension notices.
                </p>
              </div>
            </div>
            <button className="btn-secondary" onClick={handleToggleWhatsApp} disabled={togglingWhatsApp} style={{ fontSize: '0.8rem' }}>
              <span>Switch to {isRealWhatsApp ? 'Simulation' : 'Live Meta API'}</span>
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', fontSize: '0.82rem', marginBottom: '14px' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Active Mode: </span>
              <strong style={{ color: isRealWhatsApp ? '#25D366' : '#38bdf8' }}>
                {settingsData?.whatsapp_mode || 'SIMULATION'}
              </strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Phone Number ID: </span>
              <span>{settingsData?.whatsapp_phone_number_id || '(Awaiting Supervisor Key)'}</span>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Template Name: </span>
              <span><code>{settingsData?.whatsapp_template || 'service_suspension_notice'}</code></span>
            </div>
          </div>

          {/* Quick WhatsApp Test Input */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Test Dispatch:</span>
            <input
              type="text"
              className="search-input"
              value={testNumber}
              onChange={(e) => setTestNumber(e.target.value)}
              placeholder="+94770000001"
              style={{ width: '180px', padding: '6px 10px', fontSize: '0.8rem' }}
            />
            <button
              className="btn-secondary"
              onClick={handleTestWhatsApp}
              disabled={testingWhatsApp}
              style={{ fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Send size={13} />
              <span>{testingWhatsApp ? 'Sending...' : 'Send Test WhatsApp'}</span>
            </button>
          </div>
        </div>

        {/* LLM Status Card */}
        <div style={{ background: 'var(--bg-elevated)', padding: '18px 20px', borderRadius: 'var(--radius-md)', marginBottom: '16px', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <Cpu size={18} color="#94a3b8" />
            <div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Message Generation Engine</h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                Template formatting engine with optional AI content personalization.
              </p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', fontSize: '0.82rem' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Engine Status: </span>
              <strong style={{ color: settingsData?.llm_status === 'ENABLED' ? '#34d399' : '#94a3b8' }}>
                {settingsData?.llm_status === 'ENABLED' ? 'AI Dynamic Phrasing' : 'Deterministic Telecom Templates'}
              </strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Active Provider: </span>
              <span>{settingsData?.llm_provider || 'Built-in Templates'}</span>
            </div>
          </div>
        </div>

        {/* Dataset Controls Card */}
        <div style={{ background: 'var(--bg-elevated)', padding: '18px 20px', borderRadius: 'var(--radius-md)', marginBottom: '16px', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Database size={18} color="#94a3b8" />
              <div>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Customer Data Repository</h3>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  Active Storage: <code style={{ color: '#94a3b8' }}>{settingsData?.dataset_path || 'data/customers.csv'}</code>
                </p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <button 
                className="btn-secondary" 
                onClick={handleClearCache} 
                disabled={clearingCache} 
                id="clear-cache-btn" 
                style={{ fontSize: '0.8rem' }}
                title="Reset duplicate prevention cache so all accounts receive notifications fresh"
              >
                <RotateCcw size={13} className={clearingCache ? 'spin-anim' : ''} />
                <span>{clearingCache ? 'Clearing...' : 'Clear Notification Cache'}</span>
              </button>
              <button className="btn-secondary" onClick={handleClearDataset} disabled={clearingDataset} id="clear-dataset-btn" style={{ fontSize: '0.8rem' }}>
                <Trash2 size={13} className={clearingDataset ? 'spin-anim' : ''} />
                <span>{clearingDataset ? 'Clearing...' : 'Clear Customer Dataset'}</span>
              </button>
            </div>
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            To import and replace customer data, use <strong>"Upload New CSV"</strong> in the left sidebar. Use "Clear Notification Cache" if you need previously notified accounts to be re-evaluated and sent fresh emails without changing the dataset.
          </p>
        </div>

        {/* Note */}
        <div
          style={{
            padding: '14px 16px',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid var(--border-subtle)',
            fontSize: '0.8rem',
            color: 'var(--text-secondary)',
            display: 'flex',
            gap: '10px',
            alignItems: 'center',
          }}
        >
          <Info size={16} color="#94a3b8" style={{ flexShrink: 0 }} />
          <div>
            System is configured with safe duplicate prevention: accounts will receive exactly one notification per distinct suspension event.
          </div>
        </div>
      </div>
    </div>
  );
}
