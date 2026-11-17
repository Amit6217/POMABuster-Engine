import React, { useState } from 'react';
import { Search, Filter, AlertOctagon, Split, ExternalLink, ArrowRight, ShieldCheck, ChevronRight } from 'lucide-react';
import { POMAIncident, POMType } from '../types';

interface AttackTableProps {
  incidents: POMAIncident[];
  onSelectIncident: (incident: POMAIncident) => void;
}

export const AttackTable: React.FC<AttackTableProps> = ({ incidents, onSelectIncident }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('ALL');

  const filtered = incidents.filter((inc) => {
    // Search term check
    const matchesSearch =
      inc.incident_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.pom_token_symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.pom_tx_hash.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.arb_tx_hash.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.pom_operator.toLowerCase().includes(searchTerm.toLowerCase());

    if (!matchesSearch) return false;

    // Filter type check
    if (filterType === 'ALL') return true;
    if (filterType === 'DOMINATION') return inc.attack_type === 'MARKET_DOMINATION';
    if (filterType === 'WASH_SALE') return inc.attack_type === 'WASH_SALE';
    if (filterType === 'MULTI_TX') return inc.is_multi_tx;
    if (filterType === 'SINGLE_TX') return !inc.is_multi_tx;

    return true;
  });

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      {/* Table Controls Header */}
      <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by token, tx hash, or address..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-rose-500"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 sm:pb-0">
          {[
            { id: 'ALL', label: `All (${incidents.length})` },
            { id: 'MULTI_TX', label: `Multi-Tx (${incidents.filter((i) => i.is_multi_tx).length})` },
            { id: 'SINGLE_TX', label: `Single-Tx (${incidents.filter((i) => !i.is_multi_tx).length})` },
            { id: 'DOMINATION', label: 'Domination' },
            { id: 'WASH_SALE', label: 'Wash Sale' },
          ].map((pill) => (
            <button
              key={pill.id}
              onClick={() => setFilterType(pill.id)}
              className={`px-2.5 py-1 text-xs rounded-lg whitespace-nowrap transition ${
                filterType === pill.id
                  ? 'bg-rose-500 text-white font-semibold'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {pill.label}
            </button>
          ))}
        </div>
      </div>

      {/* Incidents Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/60 text-slate-400 font-semibold border-b border-slate-800">
            <tr>
              <th className="py-3 px-4">Attack Incident</th>
              <th className="py-3 px-4">Execution Type</th>
              <th className="py-3 px-4">Manipulated Asset</th>
              <th className="py-3 px-4">Extracted Profit</th>
              <th className="py-3 px-4">Intermediary Token Link</th>
              <th className="py-3 px-4">Price Impact</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-500">
                  No Price Oracle Manipulation attacks matched your filter.
                </td>
              </tr>
            ) : (
              filtered.map((inc) => (
                <tr
                  key={inc.incident_id}
                  className="hover:bg-slate-800/40 transition group cursor-pointer"
                  onClick={() => onSelectIncident(inc)}
                >
                  {/* Incident & Rule */}
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <div
                        className={`w-2 h-2 rounded-full ${
                          inc.attack_type === 'MARKET_DOMINATION' ? 'bg-rose-500' : 'bg-amber-500'
                        }`}
                      />
                      <div>
                        <div className="font-semibold text-white">
                          {inc.attack_type === 'MARKET_DOMINATION' ? 'Market Domination' : 'Wash Sale'}
                        </div>
                        <div className="font-mono text-[10px] text-slate-400">
                          {inc.incident_id.slice(0, 22)}...
                        </div>
                      </div>
                    </div>
                  </td>

                  {/* Multi-Tx vs Single-Tx */}
                  <td className="py-3 px-4">
                    {inc.is_multi_tx ? (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/10 text-rose-300 border border-rose-500/20">
                        <Split className="w-3 h-3" />
                        <span>
                          {inc.block_distance === 0
                            ? 'Same Block (Bundle)'
                            : `+${inc.block_distance} Block${inc.block_distance > 1 ? 's' : ''}`}
                        </span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                        Single-Tx (Atomic)
                      </span>
                    )}
                  </td>

                  {/* Manipulated Asset */}
                  <td className="py-3 px-4">
                    <div className="font-medium text-slate-200">
                      {inc.pom_amount.toLocaleString(undefined, { maximumFractionDigits: 2 })} {inc.pom_token_symbol}
                    </div>
                    <div className="text-[10px] font-mono text-rose-400">
                      {(inc.pom_supply_percentage * 100).toFixed(4)}% of supply
                    </div>
                  </td>

                  {/* Arbitrage Profit */}
                  <td className="py-3 px-4">
                    <div className="font-semibold text-emerald-400">
                      +${inc.arb_profit_usd.toLocaleString(undefined, { maximumFractionDigits: 2 })} USD
                    </div>
                    <div className="text-[10px] font-mono text-slate-400">
                      {inc.arb_profit_amount.toFixed(3)} {inc.arb_profit_token}
                    </div>
                  </td>

                  {/* Shared Token Link */}
                  <td className="py-3 px-4">
                    <div className="flex flex-wrap gap-1">
                      {inc.shared_tokens.map((token) => (
                        <span
                          key={token}
                          className="px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30"
                        >
                          {token}
                        </span>
                      ))}
                    </div>
                  </td>

                  {/* Price Impact */}
                  <td className="py-3 px-4">
                    <span className="font-mono text-xs font-semibold text-amber-400">
                      ~{(inc.estimated_price_impact_pct * 100).toFixed(1)}%
                    </span>
                  </td>

                  {/* Actions */}
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectIncident(inc);
                      }}
                      className="px-2.5 py-1 bg-slate-800 hover:bg-rose-500 hover:text-white text-slate-300 rounded-lg text-xs font-medium transition flex items-center space-x-1 ml-auto"
                    >
                      <span>Deep Trace</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
