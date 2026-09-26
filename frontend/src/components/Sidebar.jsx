import React from 'react';
import { 
  Activity, Users, UserX, Mail, History, Settings, 
  UploadCloud, Sun, Moon, Play, RefreshCw, X, Radio
} from 'lucide-react';
import sltLogoDark from '../assets/slt-mobitel-logo.png';
import sltLogoLight from '../assets/slt-mobitel-logo-light.png';

export default function Sidebar({ 
  activeTab, 
  setActiveTab, 
  stats, 
  settingsData, 
  onOpenUpload, 
  theme = 'dark', 
  onToggleTheme,
  agentRunning,
  onRunAgent,
  mobileOpen = false,
  onCloseMobile
}) {
  const navItems = [
    { 
      id: 'dashboard', 
      label: 'Dashboard', 
      icon: Activity, 
      badge: null 
    },
    { 
      id: 'customers', 
      label: 'Customer Accounts', 
      icon: Users, 
      badge: stats?.total_customers 
    },
    { 
      id: 'suspended', 
      label: 'Suspended Queue', 
      icon: UserX, 
      badge: stats?.suspended_customers, 
      badgeType: 'danger' 
    },
    { 
      id: 'notifications', 
      label: 'Dispatch Logs', 
      icon: Mail, 
      badge: stats?.notifications_sent, 
      badgeType: 'primary' 
    },
    { 
      id: 'runs', 
      label: 'Execution Runs', 
      icon: History, 
      badge: stats?.total_agent_runs 
    },
    { 
      id: 'settings', 
      label: 'Settings', 
      icon: Settings, 
      badge: null 
    },
  ];

  const isRealSmtp = settingsData?.email_mode === 'REAL_SMTP';

  const handleNavClick = (id) => {
    setActiveTab(id);
    if (onCloseMobile) {
      onCloseMobile();
    }
  };

  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <div 
          className="sidebar-backdrop" 
          onClick={onCloseMobile}
          aria-hidden="true" 
        />
      )}

      <aside className={`app-sidebar ${mobileOpen ? 'open' : ''}`}>
        {/* Brand / Logo Header */}
        <div className="sidebar-brand-wrapper">
          <div 
            className="sidebar-brand"
            onClick={() => handleNavClick('dashboard')}
            style={{ cursor: 'pointer' }}
          >
            <img 
              src={theme === 'light' ? sltLogoLight : sltLogoDark} 
              alt="SLT-MOBITEL Logo" 
              className="sidebar-logo-img"
            />
            <div className="sidebar-brand-text">
              <span className="sidebar-brand-title">Suspension AI</span>
              <span className="sidebar-brand-subtitle">SLT-MOBITEL AGENT</span>
            </div>
          </div>
          {onCloseMobile && (
            <button 
              className="sidebar-mobile-close-btn" 
              onClick={onCloseMobile}
              aria-label="Close menu"
            >
              <X size={18} />
            </button>
          )}
        </div>

        {/* Primary Action Button */}
        {onOpenUpload && (
          <div className="sidebar-action-wrap">
            <button
              className="sidebar-upload-btn"
              onClick={() => {
                onOpenUpload();
                if (onCloseMobile) onCloseMobile();
              }}
              title="Import Customer CSV Dataset"
              id="sidebar-upload-dataset-btn"
            >
              <UploadCloud size={16} />
              <span>Upload New CSV</span>
            </button>
          </div>
        )}

        {/* Navigation Section */}
        <div className="sidebar-nav-container">
          <div className="sidebar-nav-label">NAVIGATION</div>
          <ul className="sidebar-nav-list">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <li key={item.id}>
                  <button
                    className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
                    onClick={() => handleNavClick(item.id)}
                    id={`sidebar-nav-${item.id}`}
                  >
                    <Icon size={17} className="sidebar-nav-icon" />
                    <span className="sidebar-nav-text">{item.label}</span>
                    {item.badge !== undefined && item.badge !== null && item.badge > 0 && (
                      <span className={`sidebar-badge ${item.badgeType === 'danger' ? 'sidebar-badge-danger' : 'sidebar-badge-default'}`}>
                        {item.badge}
                      </span>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>

        {/* Bottom Status & Controls */}
        <div className="sidebar-footer">
          {/* Email Delivery Gateway Status */}
          <div className="sidebar-status-box">
            <div className="sidebar-status-header">
              <span className="sidebar-status-label">OUTBOUND GATEWAY</span>
              <div 
                className="sidebar-status-pill"
                style={{
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
                <span>{isRealSmtp ? 'SMTP Live' : 'Simulation'}</span>
              </div>
            </div>
            <div className="sidebar-status-subtext">
              {isRealSmtp ? 'Emails dispatched to live recipients' : 'Simulating dispatch safely'}
            </div>
          </div>

          {/* Theme & Profile Controls */}
          <div className="sidebar-controls-row">
            <button
              className="sidebar-theme-toggle"
              onClick={onToggleTheme}
              title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
              id="sidebar-theme-toggle-btn"
            >
              {theme === 'dark' ? (
                <>
                  <Sun size={14} color="#F59E0B" />
                  <span>Light Mode</span>
                </>
              ) : (
                <>
                  <Moon size={14} color="#005BAC" />
                  <span>Dark Mode</span>
                </>
              )}
            </button>
          </div>

          <div className="sidebar-copyright">
            Intelligent Customer Suspension Agent • POC v1.0
          </div>
        </div>
      </aside>
    </>
  );
}
