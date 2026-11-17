import React, { useState } from 'react';
import { Trade, TransferLog } from '../types';
import { Layers, ArrowRight, Database, FileText } from 'lucide-react';

interface TradesTableProps {
  trades: Trade[];
  logs: TransferLog[];
}

export const TradesTable: React.FC<TradesTableProps> = ({ trades, logs }) => {
  const [subTab, setSubTab] = useState<'trades' | 'logs'>('trades');

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      {/* Sub-tab switcher */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex space-x-2">
          <button
            onClick={() => setSubTab('trades')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition flex items-center space-x-1.5 ${
              subTab === 'trades'
                ? 'bg-rose-500 text-white shadow-sm shadow-rose-500/30'
                : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Algorithm 1: Reconstructed Trades ({trades.length})</span>
          </button>
          <button
            onClick={() => setSubTab('logs')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition flex items-center space-x-1.5 ${
              subTab === 'logs'
                ? 'bg-rose-500 text-white shadow-sm shadow-rose-500/30'
                : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Raw ERC-20 Transfer Logs ({logs.length})</span>
          </button>
        </div>
        <span className="text-xs text-slate-500 font-mono hidden sm:block">
          Definition 1: r(l1) = s(l2) & k(l1) ≠ k(l2)
        </span>
      </div>

      {subTab === 'trades' ? (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Trade ID</th>
                <th className="py-3 px-4">Block / Tx</th>
                <th className="py-3 px-4">Operator</th>
                <th className="py-3 px-4">Input Transfer</th>
                <th className="py-3 px-4">DEX Liquidity Pool</th>
                <th className="py-3 px-4">Output Transfer</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {trades.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500 font-sans">
                    No trades reconstructed yet. Run detection to reconstruct trades.
                  </td>
                </tr>
              ) : (
                trades.map((t) => (
                  <tr key={t.trade_id} className="hover:bg-slate-800/30 transition">
                    <td className="py-2.5 px-4 text-slate-300 font-semibold">{t.trade_id}</td>
                    <td className="py-2.5 px-4">
                      <div className="text-slate-200">#{t.block_number}</div>
                      <div className="text-[10px] text-slate-500 truncate max-w-[120px]" title={t.tx_hash}>
                        {t.tx_hash.slice(0, 10)}...
                      </div>
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 truncate max-w-[120px]" title={t.operator}>
                      {t.operator.slice(0, 10)}...
                    </td>
                    <td className="py-2.5 px-4 text-rose-400 font-medium">
                      -{t.amount_in.toLocaleString()} {t.token_in_symbol}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 truncate max-w-[140px]" title={t.pool_address}>
                      {t.pool_address.slice(0, 10)}...
                    </td>
                    <td className="py-2.5 px-4 text-emerald-400 font-medium">
                      +{t.amount_out.toLocaleString()} {t.token_out_symbol}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Index</th>
                <th className="py-3 px-4">Block / Tx</th>
                <th className="py-3 px-4">Sender s(l)</th>
                <th className="py-3 px-4">Receiver r(l)</th>
                <th className="py-3 px-4">Token k(l)</th>
                <th className="py-3 px-4 text-right">Amount m(l)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {logs.map((l, idx) => (
                <tr key={`${l.tx_hash}_${l.log_index}_${idx}`} className="hover:bg-slate-800/30 transition">
                  <td className="py-2.5 px-4 text-slate-500">#{l.log_index}</td>
                  <td className="py-2.5 px-4">
                    <span className="text-slate-300">#{l.block_number}</span>
                    <span className="text-slate-600 ml-1">({l.tx_hash.slice(0, 8)}...)</span>
                  </td>
                  <td className="py-2.5 px-4 text-slate-400 truncate max-w-[130px]" title={l.sender}>
                    {l.sender.slice(0, 10)}...
                  </td>
                  <td className="py-2.5 px-4 text-slate-400 truncate max-w-[130px]" title={l.receiver}>
                    {l.receiver.slice(0, 10)}...
                  </td>
                  <td className="py-2.5 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-200">
                      {l.token_symbol}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-right text-slate-200 font-semibold">
                    {l.amount.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
