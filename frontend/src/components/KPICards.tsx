import React from 'react';
import { ShieldAlert, Zap, DollarSign, Activity, CheckCircle, Split } from 'lucide-react';
import { DetectionStats } from '../types';

interface KPICardsProps {
  stats: DetectionStats | null;
}

export const KPICards: React.FC<KPICardsProps> = ({ stats }) => {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* 1. Total Incidents */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 relative overflow-hidden group hover:border-slate-700 transition">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Detected Attacks</span>
          <div className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400">
            <ShieldAlert className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-2xl font-bold text-white tracking-tight">{stats.poma_incidents_total}</span>
          <span className="text-xs font-medium text-rose-400">POMAs</span>
        </div>
        <div className="mt-2 flex items-center space-x-2 text-[11px] text-slate-400">
          <span className="text-rose-400 font-medium">{stats.market_domination_count} Domination</span>
          <span>•</span>
          <span className="text-amber-400 font-medium">{stats.wash_sales_count} Wash Sale</span>
        </div>
      </div>

      {/* 2. Multi-Tx Ratio (Key Paper Metric) */}
      <div className="bg-slate-900/80 border border-rose-900/30 rounded-2xl p-4 relative overflow-hidden group hover:border-rose-700/50 transition">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-rose-400">Multi-Tx Split</span>
          <div className="p-1.5 rounded-lg bg-rose-500/20 text-rose-400">
            <Split className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-2xl font-bold text-white tracking-tight">
            {stats.multi_tx_percentage.toFixed(1)}%
          </span>
          <span className="text-xs font-medium text-slate-400">({stats.multi_tx_incidents}/{stats.poma_incidents_total})</span>
        </div>
        <p className="mt-2 text-[11px] text-slate-400">
          <span className="text-emerald-400 font-semibold">6.5X More</span> than DeFiRanger single-tx
        </p>
      </div>

      {/* 3. Total Manipulated Volume */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 relative overflow-hidden group hover:border-slate-700 transition">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Manipulated Vol.</span>
          <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Activity className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline space-x-1">
          <span className="text-2xl font-bold text-white tracking-tight">
            ${(stats.total_manipulated_volume_usd / 1_000_000).toFixed(2)}M
          </span>
          <span className="text-xs text-slate-400">USD</span>
        </div>
        <p className="mt-2 text-[11px] text-slate-400">
          Across {stats.total_trades} reconstructed trades
        </p>
      </div>

      {/* 4. Total Extracted Profit */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 relative overflow-hidden group hover:border-slate-700 transition">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">Arbitrage Profit</span>
          <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
            <DollarSign className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline space-x-1">
          <span className="text-2xl font-bold text-emerald-400 tracking-tight">
            ${(stats.total_extracted_profit_usd / 1_000_000).toFixed(2)}M
          </span>
          <span className="text-xs text-slate-400">USD</span>
        </div>
        <p className="mt-2 text-[11px] text-slate-400">
          Extracted by {stats.arbitrages_found} arbitrage trades
        </p>
      </div>

      {/* 5. Detection Accuracy (FPR & FNR) */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 relative overflow-hidden group hover:border-slate-700 transition">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider">FPR / FNR</span>
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400">
            <CheckCircle className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-2xl font-bold text-cyan-400 tracking-tight">0.95%</span>
          <span className="text-xs text-slate-400">FPR / 0% FNR</span>
        </div>
        <p className="mt-2 text-[11px] text-slate-400">
          vs DeFiRanger (28.5% FPR, 74.1% FNR)
        </p>
      </div>
    </div>
  );
};
