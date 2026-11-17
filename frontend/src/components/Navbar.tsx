import React from 'react';
import { ShieldAlert, RefreshCw, RotateCcw, Cpu, CheckCircle2, Layers } from 'lucide-react';
import { SystemConfig } from '../types';

interface NavbarProps {
  config: SystemConfig | null;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onDetect: () => void;
  onReset: () => void;
  isScanning: boolean;
  isConnected: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  config,
  activeTab,
  setActiveTab,
  onDetect,
  onReset,
  isScanning,
  isConnected,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Paper Reference */}
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400">
              <ShieldAlert className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl tracking-tight text-white">
                  POMA<span className="text-rose-500">Buster</span>
                </span>
                <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30">
                  IEEE S&P '24
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Price Oracle Manipulation Attack Detector in DeFi
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex space-x-1 bg-slate-950 p-1 rounded-xl border border-slate-800/80">
            {[
              { id: 'incidents', label: 'Attacks & Incidents' },
              { id: 'analytics', label: 'Paper Analytics' },
              { id: 'trades', label: 'Reconstructed Trades' },
              { id: 'tokens', label: 'Token Registry' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                  activeTab === tab.id
                    ? 'bg-rose-500 text-white shadow-sm shadow-rose-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          {/* Controls & Connection */}
          <div className="flex items-center space-x-3">
            {/* Status Indicator */}
            <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-xs">
              <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-amber-500 animate-ping'}`} />
              <span className="text-slate-400">{isConnected ? 'Engine Online' : 'Connecting...'}</span>
            </div>

            {/* Threshold Pill */}
            {config && (
              <div className="hidden md:flex items-center space-x-2 px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300">
                <span className="text-slate-500">σ:</span>
                <span className="text-rose-400 font-semibold">{(config.sigma * 100).toFixed(3)}%</span>
                <span className="text-slate-700">|</span>
                <span className="text-slate-500">n:</span>
                <span className="text-cyan-400 font-semibold">{config.block_window_n} blks</span>
              </div>
            )}

            {/* Reset Button */}
            <button
              onClick={onReset}
              title="Reset Database to Paper Benchmark Dataset"
              className="p-2 text-slate-400 hover:text-white bg-slate-800/70 hover:bg-slate-800 rounded-lg border border-slate-700 transition"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            {/* Run Scan Button */}
            <button
              onClick={onDetect}
              disabled={isScanning}
              className="flex items-center space-x-1.5 px-3 py-2 bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 text-white text-xs font-semibold rounded-lg shadow-sm shadow-rose-600/30 disabled:opacity-50 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : ''}`} />
              <span>{isScanning ? 'Scanning...' : 'Re-Run Detection'}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
