import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell,
  PieChart, Pie, Legend
} from 'recharts';
import { DetectionStats } from '../types';
import { TrendingUp, BarChart3, PieChart as PieIcon, ShieldAlert } from 'lucide-react';

interface AnalyticsChartsProps {
  stats: DetectionStats | null;
}

const COLORS = ['#f43f5e', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

export const AnalyticsCharts: React.FC<AnalyticsChartsProps> = ({ stats }) => {
  if (!stats) return null;

  // 1. Target Asset Data (matching Paper Figure 5a)
  const assetData = stats.top_assets_targeted.length > 0
    ? stats.top_assets_targeted
    : [
        { symbol: 'WETH', count: 11997, percentage: 72.4 },
        { symbol: 'USDC', count: 6023, percentage: 36.3 },
        { symbol: 'WBTC', count: 4115, percentage: 24.8 },
        { symbol: 'USDT', count: 3350, percentage: 20.2 },
        { symbol: 'DAI', count: 3315, percentage: 20.0 },
      ];

  // 2. Block Time Span Distribution (matching Paper Table 1)
  const timeSpanData = [
    { name: 'Same-Tx (n = -1)', count: stats.block_time_distribution['-1'] || 1, pct: '4.1%' },
    { name: 'Same Block (n = 0)', count: stats.block_time_distribution['0'] || 4, pct: '92.1%' },
    { name: 'Block +1 (n = 1)', count: stats.block_time_distribution['1'] || 2, pct: '2.5%' },
    { name: 'Block +2 (n = 2)', count: stats.block_time_distribution['2'] || 1, pct: '0.0%' },
  ];

  // 3. Comparison with Prior Work (Table 2)
  const toolComparison = [
    { name: 'POMABuster (All)', detected: 16581, fpr: 0.95, time: 67.9 },
    { name: 'POMABuster-Single', detected: 4279, fpr: 0.95, time: 8.5 },
    { name: 'DeFiRanger (Prior)', detected: 5371, fpr: 28.58, time: 85.0 },
  ];

  // 4. Operator Concentration Data (Figure 5b)
  const operatorData = stats.top_operators.length > 0
    ? stats.top_operators.map((op, idx) => ({
        address: `${op.address.slice(0, 8)}...`,
        profit: op.profit_usd,
      }))
    : [
        { address: '0x56178a...', profit: 3150000 },
        { address: '0x111111...', profit: 10264 },
        { address: '0x444444...', profit: 37740 },
        { address: '0x777777...', profit: 17136 },
      ];

  return (
    <div className="space-y-6">
      {/* Top Row: Asset Distribution & Time Span */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Asset Distribution */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4 text-rose-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Target Assets Involved in POMAs (Paper Fig. 5a)
              </h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">Long-Tail Distribution</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={assetData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="symbol" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff', fontWeight: 'bold' }}
                />
                <Bar dataKey="count" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            WETH is the dominant target (used in over 70% of attacks), followed by stablecoins (USDC, DAI, USDT) and WBTC.
          </p>
        </div>

        {/* Block Time Span Distribution (Table 1) */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <PieIcon className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Time Span Between POM & Arbitrage (Paper Table 1)
              </h3>
            </div>
            <span className="text-xs text-cyan-400 font-mono font-semibold">98.7% within n ≤ 2</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={timeSpanData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff', fontWeight: 'bold' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {timeSpanData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            92.1% occur in the same block via Flashbots bundles (n = 0), and 2.5% in consecutive blocks. Prior single-tx tools miss 95.9% of these.
          </p>
        </div>
      </div>

      {/* Bottom Row: Tool Comparison & Operator Concentration */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tool Comparison */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Comparison with DeFiRanger (Paper Table 2)
              </h3>
            </div>
            <span className="text-xs text-emerald-400 font-mono">6.5X Detection Gain</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={toolComparison} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff', fontWeight: 'bold' }}
                />
                <Bar dataKey="detected" fill="#10b981" radius={[4, 4, 0, 0]} name="Detected Attacks" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
            <div className="p-2 bg-slate-950 rounded-lg border border-slate-800">
              <div className="text-slate-400 text-[10px]">POMABuster FPR</div>
              <div className="text-emerald-400 font-bold">0.95%</div>
            </div>
            <div className="p-2 bg-slate-950 rounded-lg border border-slate-800">
              <div className="text-slate-400 text-[10px]">DeFiRanger FPR</div>
              <div className="text-rose-400 font-bold">28.58%</div>
            </div>
            <div className="p-2 bg-slate-950 rounded-lg border border-slate-800">
              <div className="text-slate-400 text-[10px]">DeFiRanger FNR</div>
              <div className="text-amber-400 font-bold">74.10%</div>
            </div>
          </div>
        </div>

        {/* Operator Concentration */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Top Operator Profit Concentration (Section 4.7)
              </h3>
            </div>
            <span className="text-xs text-amber-400 font-mono">&gt;95% Address Reuse</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={operatorData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="address" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff', fontWeight: 'bold' }}
                  formatter={(val: any) => [`$${Number(val).toLocaleString()} USD`, 'Profit Realized']}
                />
                <Bar dataKey="profit" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            More than 95% of attacker addresses were reused across multiple transactions, enabling address-based tracking and CEX deposit deanonymization.
          </p>
        </div>
      </div>
    </div>
  );
};
