import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { KPICards } from './components/KPICards';
import { ConfigPanel } from './components/ConfigPanel';
import { AttackTable } from './components/AttackTable';
import { AttackDetailModal } from './components/AttackDetailModal';
import { AnalyticsCharts } from './components/AnalyticsCharts';
import { TradesTable } from './components/TradesTable';
import { TokenList } from './components/TokenList';
import { POMAIncident, DetectionStats, SystemConfig, Trade, TransferLog, TokenInfo } from './types';
import { ShieldAlert, AlertCircle, Info } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('incidents');
  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [stats, setStats] = useState<DetectionStats | null>(null);
  const [incidents, setIncidents] = useState<POMAIncident[]>([]);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [logs, setLogs] = useState<TransferLog[]>([]);
  const [tokens, setTokens] = useState<TokenInfo[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<POMAIncident | null>(null);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Fetch initial data
  const loadData = async () => {
    try {
      const [cfgRes, statsRes, incRes, tradesRes, logsRes, tokensRes] = await Promise.all([
        fetch('/api/config'),
        fetch('/api/stats'),
        fetch('/api/incidents'),
        fetch('/api/trades'),
        fetch('/api/logs'),
        fetch('/api/tokens'),
      ]);

      if (cfgRes.ok) setConfig(await cfgRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
      if (incRes.ok) setIncidents(await incRes.json());
      if (tradesRes.ok) setTrades(await tradesRes.json());
      if (logsRes.ok) setLogs(await logsRes.json());
      if (tokensRes.ok) setTokens(await tokensRes.json());

      setIsConnected(true);
    } catch (err) {
      console.error('Error connecting to backend:', err);
      setIsConnected(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Re-run detection with active or new parameters
  const handleDetect = async (customSigma?: number, customN?: number, customStrike?: number) => {
    setIsScanning(true);
    try {
      const body: any = {};
      if (customSigma !== undefined) body.sigma = customSigma;
      if (customN !== undefined) body.block_window_n = customN;
      if (customStrike !== undefined) body.strike_percentage = customStrike;

      const res = await fetch('/api/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (res.ok) {
        const data = await res.json();
        setStats(data.stats);
        setIncidents(data.incidents);
        // Refresh trades and config
        const [tradesRes, cfgRes] = await Promise.all([fetch('/api/trades'), fetch('/api/config')]);
        if (tradesRes.ok) setTrades(await tradesRes.json());
        if (cfgRes.ok) setConfig(await cfgRes.json());

        showToast(`Detection complete! Flagged ${data.incidents_count} POMA attack incidents.`);
      }
    } catch (err) {
      console.error('Error running detection:', err);
      showToast('Error communicating with detection engine.');
    } finally {
      setIsScanning(false);
    }
  };

  // Reset to canonical benchmark dataset
  const handleReset = async () => {
    setIsScanning(true);
    try {
      const res = await fetch('/api/reset-demo', { method: 'POST' });
      if (res.ok) {
        await loadData();
        showToast('Benchmark dataset reloaded and re-analyzed.');
      }
    } catch (err) {
      console.error('Error resetting:', err);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-rose-600 text-white px-4 py-2.5 rounded-xl shadow-2xl text-xs font-semibold flex items-center space-x-2 animate-bounce">
          <Info className="w-4 h-4" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Navbar */}
      <Navbar
        config={config}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onDetect={() => handleDetect()}
        onReset={handleReset}
        isScanning={isScanning}
        isConnected={isConnected}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* KPI Metrics Banner */}
        <KPICards stats={stats} />

        {/* Threshold Configuration Drawer */}
        {config && (
          <ConfigPanel
            config={config}
            onApplyConfig={(sigma, n, strike) => handleDetect(sigma, n, strike)}
            isScanning={isScanning}
          />
        )}

        {/* Tab Content */}
        {activeTab === 'incidents' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white tracking-tight">
                  Detected Price Oracle Manipulation Attacks
                </h2>
                <p className="text-xs text-slate-400">
                  Linked across transactions using SEC Market Domination and Wash Sale rules (Definition 3, 5, 6 & 7)
                </p>
              </div>
              <span className="text-xs font-mono text-slate-400">
                {incidents.length} incident{incidents.length === 1 ? '' : 's'} flagged
              </span>
            </div>

            <AttackTable
              incidents={incidents}
              onSelectIncident={(inc) => setSelectedIncident(inc)}
            />
          </div>
        )}

        {activeTab === 'analytics' && <AnalyticsCharts stats={stats} />}

        {activeTab === 'trades' && <TradesTable trades={trades} logs={logs} />}

        {activeTab === 'tokens' && <TokenList tokens={tokens} sigma={config ? config.sigma : 0.0001} />}
      </main>

      {/* Deep-Dive Attack Modal */}
      <AttackDetailModal
        incident={selectedIncident}
        onClose={() => setSelectedIncident(null)}
      />

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500">
        <p>
          Recreating <strong className="text-slate-400">"POMABuster: Detecting Price Oracle Manipulation Attacks in Decentralized Finance"</strong> (IEEE S&P 2024).
        </p>
      </footer>
    </div>
  );
};

export default App;
