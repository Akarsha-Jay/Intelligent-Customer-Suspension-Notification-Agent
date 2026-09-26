import React from 'react';
import { Activity, Users, Mail, Settings, UploadCloud, Sun, Moon } from 'lucide-react';
import sltLogoDark from '../assets/slt-mobitel-logo.png';
import sltLogoLight from '../assets/slt-mobitel-logo-light.png';

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  settingsData, 
  onOpenUpload, 
  theme = 'dark', 
  onToggleTheme 
}) {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'customers', label: 'Customer Accounts', icon: Users },
    { id: 'notifications', label: 'Dispatch Logs', icon: Mail },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const isRealSmtp = settingsData?.email_mode === 'REAL_SMTP';

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        {/* Official SLT-MOBITEL Branding Section */}
        <div 
          className="brand-section" 
          onClick={() => setActiveTab('dashboard')} 
          style={{ cursor: 'pointer' }}
        >
          <img 
            src={theme === 'light' ? sltLogoLight : sltLogoDark} 
            alt="SLT-MOBITEL Logo" 
            className="slt-logo-img"
          />
          <div className="brand-divider" />
          <div className="brand-text">
            <span className="brand-title">Suspension AI</span>
            <span className="brand-tag">POC v1.0 • Intelligent Notification Engine</span>
          </div>
        </div>

        {/* Primary Navigation Tabs */}
        <ul className="nav-links">
          {tabs.map((t) => {
            const Icon = t.icon;
            const isActive = activeTab === t.id;
            return (
              <li key={t.id}>
                <button
                  className={`nav-btn ${isActive ? 'active' : ''}`}
                  onClick={() => setActiveTab(t.id)}
                  id={`nav-btn-${t.id}`}
                >
                  <Icon size={15} />
                  <span>{t.label}</span>
                </button>
              </li>
            );
          })}
        </ul>

        {/* Global Controls & Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Theme Toggle Button */}
          <button
            className="theme-toggle-btn"
            onClick={onToggleTheme}
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
            id="theme-toggle-btn"
          >
            {theme === 'dark' ? (
              <>
                <Sun size={14} color="#F59E0B" />
                <span>Light</span>
              </>
            ) : (
              <>
                <Moon size={14} color="#005BAC" />
                <span>Dark</span>
              </>
            )}
          </button>

          {onOpenUpload && (
            <button
              className="btn-secondary"
              onClick={onOpenUpload}
              title="Import Customer CSV Dataset"
              id="navbar-upload-dataset-btn"
            >
              <UploadCloud size={14} color="var(--text-secondary)" />
              <span>Upload Dataset</span>
            </button>
          )}

          {/* Mail Mode Badge */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.76rem',
              fontWeight: 600,
              padding: '4px 10px',
              borderRadius: 'var(--radius-md)',
              background: isRealSmtp ? 'var(--mobitel-green-tint)' : 'rgba(0, 144, 208, 0.12)',
              color: isRealSmtp ? 'var(--mobitel-green)' : 'var(--slt-cyan)',
              border: `1px solid ${isRealSmtp ? 'var(--mobitel-green-border)' : 'rgba(0, 144, 208, 0.25)'}`,
            }}
          >
            <span
              style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: isRealSmtp ? 'var(--mobitel-green)' : 'var(--slt-cyan)',
              }}
            />
            <span>{isRealSmtp ? 'SMTP Live' : 'Simulation Mode'}</span>
          </div>
        </div>
      </div>
    </nav>
  );
}
