import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import CustomersPage from './pages/CustomersPage';
import SuspendedPage from './pages/SuspendedPage';
import NotificationsPage from './pages/NotificationsPage';
import AgentRunsPage from './pages/AgentRunsPage';
import SettingsPage from './pages/SettingsPage';
import UploadDatasetModal from './components/UploadDatasetModal';
import { fetchStats, fetchSettings, runAgent, updateChannelStrategy } from './api';
import { Menu, RefreshCw, Play, MessageSquare, Mail, Layers } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [settingsData, setSettingsData] = useState(null);
  const [agentRunning, setAgentRunning] = useState(false);
  const [bannerAlert, setBannerAlert] = useState('');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  // Theme Management (Dark / Light) with LocalStorage persistence
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('slt_theme') || 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('slt_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const loadGlobalStats = async () => {
    try {
      const [sData, cfgData] = await Promise.all([fetchStats(), fetchSettings()]);
      setStats(sData);
      setSettingsData(cfgData);
    } catch (err) {
      console.error('Error loading global stats:', err);
    }
  };

  useEffect(() => {
    loadGlobalStats();
    const interval = setInterval(loadGlobalStats, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleRunAgent = async () => {
    setAgentRunning(true);
    setBannerAlert('');
    try {
      const res = await runAgent();
      const r = res.run;
      setBannerAlert(
        `Agent Run ${r.run_id} completed: ${r.notifications_sent} sent, ${r.notifications_skipped} skipped (duplicates/inactive), ${r.notifications_failed} failed.`
      );
      await loadGlobalStats();
    } catch (err) {
      setBannerAlert(`Agent Execution Error: ${err.message}`);
    } finally {
      setAgentRunning(false);
    }
  };

  const handleUpdateStrategy = async (strategy) => {
    try {
      await updateChannelStrategy(strategy);
      const label = strategy === 'EMAIL_ONLY' ? 'Email Only' : strategy === 'WHATSAPP_ONLY' ? 'WhatsApp Only' : 'Both Channels';
      setBannerAlert(`Active notification dispatch channel updated to: ${label}`);
      await loadGlobalStats();
      setTimeout(() => setBannerAlert(''), 4000);
    } catch (err) {
      setBannerAlert(`Failed to change channel: ${err.message}`);
    }
  };

  const getPageInfo = () => {
    switch (activeTab) {
      case 'dashboard':
        return {
          title: 'Operations Dashboard',
          subtitle: 'Real-time overview of customer accounts, queue status & notification dispatches',
        };
      case 'customers':
        return {
          title: 'Customer Accounts Directory',
          subtitle: 'Browse and inspect subscriber records, contact details, and current statuses',
        };
      case 'suspended':
        return {
          title: 'Suspended Customers Queue',
          subtitle: 'Active accounts marked for suspension requiring notification decisions',
        };
      case 'notifications':
        return {
          title: 'Notification Dispatch Audit Log',
          subtitle: 'Historical record of sent, simulated, and skipped suspension email dispatches',
        };
      case 'runs':
        return {
          title: 'Agent Execution Runs',
          subtitle: 'Audit trail of batch execution cycles, evaluated counts, and performance',
        };
      case 'settings':
        return {
          title: 'System Configuration & Channels',
          subtitle: 'Outbound mail gateway, template generation engine, and data storage settings',
        };
      default:
        return {
          title: 'Intelligent Suspension Agent',
          subtitle: 'SLT-Mobitel Automated Notification Service',
        };
    }
  };

  const pageInfo = getPageInfo();
  const isAgentBusy = stats?.agent_status === 'RUNNING' || agentRunning;
  const currentStrategy = settingsData?.channel_strategy || 'BOTH';

  return (
    <div className="app-layout">
      {/* Left Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        stats={stats}
        settingsData={settingsData}
        onOpenUpload={() => setIsUploadModalOpen(true)}
        theme={theme}
        onToggleTheme={toggleTheme}
        agentRunning={agentRunning}
        onRunAgent={handleRunAgent}
        mobileOpen={mobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
      />

      {/* Main Content Shell */}
      <div className="app-main-shell">
        {/* Top Header Bar */}
        <header className="app-topbar">
          <div className="app-topbar-left">
            <button
              className="app-topbar-menu-btn"
              onClick={() => setMobileSidebarOpen(true)}
              aria-label="Open sidebar menu"
            >
              <Menu size={18} />
            </button>
            <div className="app-topbar-heading">
              <h1 className="app-topbar-title">{pageInfo.title}</h1>
              <p className="app-topbar-subtitle">{pageInfo.subtitle}</p>
            </div>
          </div>

          <div className="app-topbar-right">
            {/* Outbound Channel Strategy Selector */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: '2px',
                gap: '2px',
              }}
              title="Select which channel notifications will be dispatched through when the agent runs"
            >
              <button
                type="button"
                onClick={() => handleUpdateStrategy('WHATSAPP_ONLY')}
                disabled={isAgentBusy}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '4px 8px',
                  fontSize: '0.74rem',
                  fontWeight: currentStrategy === 'WHATSAPP_ONLY' ? 600 : 400,
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  cursor: isAgentBusy ? 'not-allowed' : 'pointer',
                  background: currentStrategy === 'WHATSAPP_ONLY' ? '#25D366' : 'transparent',
                  color: currentStrategy === 'WHATSAPP_ONLY' ? '#000' : 'var(--text-secondary)',
                  transition: 'all 0.15s ease',
                }}
                title="Send suspension notifications solely via WhatsApp"
              >
                <MessageSquare size={12} />
                <span>WhatsApp Only</span>
              </button>

              <button
                type="button"
                onClick={() => handleUpdateStrategy('EMAIL_ONLY')}
                disabled={isAgentBusy}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '4px 8px',
                  fontSize: '0.74rem',
                  fontWeight: currentStrategy === 'EMAIL_ONLY' ? 600 : 400,
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  cursor: isAgentBusy ? 'not-allowed' : 'pointer',
                  background: currentStrategy === 'EMAIL_ONLY' ? '#38bdf8' : 'transparent',
                  color: currentStrategy === 'EMAIL_ONLY' ? '#000' : 'var(--text-secondary)',
                  transition: 'all 0.15s ease',
                }}
                title="Send suspension notifications solely via Email"
              >
                <Mail size={12} />
                <span>Email Only</span>
              </button>

              <button
                type="button"
                onClick={() => handleUpdateStrategy('BOTH')}
                disabled={isAgentBusy}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '4px 8px',
                  fontSize: '0.74rem',
                  fontWeight: currentStrategy === 'BOTH' ? 600 : 400,
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  cursor: isAgentBusy ? 'not-allowed' : 'pointer',
                  background: currentStrategy === 'BOTH' ? 'var(--primary-color)' : 'transparent',
                  color: currentStrategy === 'BOTH' ? '#fff' : 'var(--text-secondary)',
                  transition: 'all 0.15s ease',
                }}
                title="Send suspension notifications to both Email and WhatsApp"
              >
                <Layers size={12} />
                <span>Both</span>
              </button>
            </div>

            {/* Quick Status Pill */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '7px',
                fontSize: '0.76rem',
                fontWeight: 600,
                padding: '4px 10px',
                borderRadius: 'var(--radius-md)',
                background: isAgentBusy ? 'rgba(0, 144, 208, 0.15)' : 'var(--mobitel-green-tint)',
                color: isAgentBusy ? 'var(--slt-cyan)' : 'var(--mobitel-green)',
                border: `1px solid ${isAgentBusy ? 'rgba(0, 144, 208, 0.3)' : 'var(--mobitel-green-border)'}`,
              }}
            >
              <span
                style={{
                  width: '7px',
                  height: '7px',
                  borderRadius: '50%',
                  background: isAgentBusy ? 'var(--slt-cyan)' : 'var(--mobitel-green)',
                }}
                className={isAgentBusy ? 'spin-anim' : ''}
              />
              <span>{isAgentBusy ? 'RUNNING BATCH' : 'AGENT READY'}</span>
            </div>

            {/* Quick Refresh */}
            <button
              className="btn-secondary"
              onClick={loadGlobalStats}
              title="Refresh Statistics"
              style={{ padding: '6px 10px', fontSize: '0.78rem' }}
            >
              <RefreshCw size={13} />
              <span>Refresh</span>
            </button>

            {/* Authoritative Single Run Agent Trigger Button */}
            <button
              className={`topbar-run-agent-btn ${isAgentBusy ? 'running' : ''}`}
              onClick={handleRunAgent}
              disabled={isAgentBusy}
              id="topbar-run-agent-btn"
              title={isAgentBusy ? 'Batch evaluation currently executing...' : `Trigger intelligent evaluation (${currentStrategy === 'WHATSAPP_ONLY' ? 'WhatsApp only' : currentStrategy === 'EMAIL_ONLY' ? 'Email only' : 'Both channels'})`}
            >
              {isAgentBusy ? (
                <>
                  <RefreshCw size={13} className="spin-anim" />
                  <span>Evaluating Queue...</span>
                </>
              ) : (
                <>
                  <Play size={13} fill="currentColor" />
                  <span>RUN AGENT</span>
                </>
              )}
            </button>
          </div>
        </header>

        {/* Toast Alert Banner */}
        {bannerAlert && (
          <div className="toast-banner">
            <div className={`toast-inner ${bannerAlert.includes('Error') ? 'toast-error' : 'toast-success'}`}>
              <span>{bannerAlert}</span>
              <button
                onClick={() => setBannerAlert('')}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'inherit',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: '1rem',
                  marginLeft: '12px',
                }}
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Main Content Workspace */}
        <main className="app-main-content">
          {activeTab === 'dashboard' && (
            <DashboardPage
              stats={stats}
              settingsData={settingsData}
              onUpdateStrategy={handleUpdateStrategy}
              onRefresh={loadGlobalStats}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === 'customers' && (
            <CustomersPage
              onStatsUpdated={loadGlobalStats}
            />
          )}

          {activeTab === 'suspended' && (
            <SuspendedPage
              onStatsUpdated={loadGlobalStats}
            />
          )}

          {activeTab === 'notifications' && (
            <NotificationsPage />
          )}

          {activeTab === 'runs' && (
            <AgentRunsPage />
          )}

          {activeTab === 'settings' && (
            <SettingsPage
              settingsData={settingsData}
              onSettingsUpdated={loadGlobalStats}
              onStatsUpdated={loadGlobalStats}
            />
          )}
        </main>
      </div>

      {/* Upload Dataset Modal */}
      {isUploadModalOpen && (
        <UploadDatasetModal
          onClose={() => setIsUploadModalOpen(false)}
          onDatasetImported={async (res) => {
            await loadGlobalStats();
            setBannerAlert(`Imported ${res.total_records} accounts (${res.suspended_records} suspended) from ${res.filename}.`);
            setActiveTab('customers');
          }}
          onRunAgentAfterImport={async () => {
            await loadGlobalStats();
            setActiveTab('suspended');
            handleRunAgent();
          }}
        />
      )}
    </div>
  );
}
