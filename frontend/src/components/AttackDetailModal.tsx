import React from 'react';
import { X, AlertTriangle, ArrowRight, CheckCircle2, Split, ShieldAlert, Cpu, ExternalLink } from 'lucide-react';
import { POMAIncident } from '../types';

interface AttackDetailModalProps {
  incident: POMAIncident | null;
  onClose: () => void;
}

export const AttackDetailModal: React.FC<AttackDetailModalProps> = ({ incident, onClose }) => {
  if (!incident) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden my-8">
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-rose-500/10 border border-rose-500/30 rounded-2xl text-rose-400">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-bold text-white tracking-tight">
                  Price Oracle Manipulation Attack (POMA) Deep Trace
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                  {incident.attack_type}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Incident ID: {incident.incident_id}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* 1. Visual Attack Flowchart */}
          <div className="bg-slate-950 rounded-2xl p-5 border border-slate-800">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center space-x-1.5">
              <Cpu className="w-4 h-4 text-rose-400" />
              <span>Attack Flow Diagram (POMABuster Algorithm 1 & 2 + Definition 7)</span>
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
              {/* Step 1: POM Transaction */}
              <div className="bg-slate-900/90 border border-rose-500/30 rounded-xl p-4 relative">
                <div className="flex items-center justify-between text-xs mb-2">
                  <span className="font-bold text-rose-400">Step 1: Oracle Tilt</span>
                  <span className="text-[10px] font-mono text-slate-400">Block #{incident.pom_block}</span>
                </div>
                <div className="text-xs font-semibold text-white mb-1">
                  {incident.pom_amount.toLocaleString()} {incident.pom_token_symbol}
                </div>
                <div className="text-[11px] text-slate-400 mb-2">
                  Exceeds {(incident.pom_supply_percentage * 100).toFixed(4)}% of circulating supply
                </div>
                <div className="text-[10px] font-mono text-slate-500 truncate" title={incident.pom_tx_hash}>
                  Tx: {incident.pom_tx_hash.slice(0, 16)}...
                </div>
                <div className="text-[10px] font-mono text-slate-500 truncate mt-0.5">
                  Op: {incident.pom_operator.slice(0, 16)}...
                </div>
              </div>

              {/* Cross-Block Linking Bridge */}
              <div className="flex flex-col items-center justify-center p-2 text-center">
                <div className="px-3 py-1 rounded-full text-[11px] font-mono font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 flex items-center space-x-1.5">
                  <Split className="w-3.5 h-3.5" />
                  <span>
                    {incident.is_multi_tx
                      ? incident.block_distance === 0
                        ? 'Flashbots Bundle (Same Block)'
                        : `Span: +${incident.block_distance} Block(s)`
                      : 'Same-Tx Atomic (n = -1)'}
                  </span>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-600 my-1 hidden md:block" />
                <span className="text-[10px] text-slate-400">
                  Shared Asset: <strong className="text-cyan-400">{incident.shared_tokens.join(', ')}</strong>
                </span>
              </div>

              {/* Step 2: Profitable Arbitrage */}
              <div className="bg-slate-900/90 border border-emerald-500/30 rounded-xl p-4">
                <div className="flex items-center justify-between text-xs mb-2">
                  <span className="font-bold text-emerald-400">Step 2: Arbitrage Harvest</span>
                  <span className="text-[10px] font-mono text-slate-400">Block #{incident.arb_block}</span>
                </div>
                <div className="text-xs font-semibold text-emerald-300 mb-1">
                  +${incident.arb_profit_usd.toLocaleString(undefined, { maximumFractionDigits: 2 })} USD
                </div>
                <div className="text-[11px] text-slate-400 mb-2">
                  Net {incident.arb_profit_amount.toFixed(4)} {incident.arb_profit_token} profit
                </div>
                <div className="text-[10px] font-mono text-slate-500 truncate" title={incident.arb_tx_hash}>
                  Tx: {incident.arb_tx_hash.slice(0, 16)}...
                </div>
                <div className="text-[10px] font-mono text-slate-500 truncate mt-0.5">
                  Op: {incident.arb_operator.slice(0, 16)}...
                </div>
              </div>
            </div>
          </div>

          {/* 2. "Why Flagged as Suspicious" Diagnostic Section */}
          <div className="bg-slate-950/60 rounded-2xl p-5 border border-slate-800 space-y-4">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-rose-400 flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4" />
              <span>Why This Transaction Was Flagged (Formal Rule Diagnostics)</span>
            </h4>

            {/* Explanation Prose */}
            <div className="p-3.5 bg-rose-500/10 border border-rose-500/20 rounded-xl text-xs text-slate-200 leading-relaxed font-sans">
              {incident.explanation}
            </div>

            {/* Rule Checklist */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 space-y-1">
                <div className="flex items-center space-x-1.5 text-emerald-400 font-semibold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>SEC Rule: {incident.attack_type}</span>
                </div>
                <p className="text-slate-400 text-[11px]">
                  Trade volume of {incident.pom_amount.toLocaleString()} {incident.pom_token_symbol} represented{' '}
                  {(incident.pom_supply_percentage * 100).toFixed(4)}% of total supply, exceeding threshold σ (
                  {(incident.pom_details.threshold_sigma * 100).toFixed(4)}%).
                </p>
              </div>

              <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 space-y-1">
                <div className="flex items-center space-x-1.5 text-emerald-400 font-semibold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Definition 6: Arbitrage Loop & Profit</span>
                </div>
                <p className="text-slate-400 text-[11px]">
                  Arbitrage transaction demonstrated non-negative delta across all tokens and strictly positive net
                  profit of +{incident.arb_profit_amount.toFixed(4)} {incident.arb_profit_token}.
                </p>
              </div>

              <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 space-y-1">
                <div className="flex items-center space-x-1.5 text-emerald-400 font-semibold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Definition 7: Token Overlap (K_MANI ∩ K_INTR)</span>
                </div>
                <p className="text-slate-400 text-[11px]">
                  Non-empty intersection on [{incident.shared_tokens.join(', ')}]. The arbitrageur used the manipulated
                  token as an intermediate asset to profit.
                </p>
              </div>

              <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 space-y-1">
                <div className="flex items-center space-x-1.5 text-emerald-400 font-semibold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Spot Price Impact Watermark</span>
                </div>
                <p className="text-slate-400 text-[11px]">
                  Estimated pool spot price deviation ~{(incident.estimated_price_impact_pct * 100).toFixed(1)}%,
                  surpassing the 2.0% strike watermark (True Positive).
                </p>
              </div>
            </div>
          </div>

          {/* 3. Deep Transaction Details & Token Addresses */}
          <div className="bg-slate-950/60 rounded-2xl p-5 border border-slate-800 text-xs font-mono space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-sans mb-3">
              Technical Blockchain Metadata
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-slate-300">
              <div>
                <span className="text-slate-500">POM Tx Hash: </span>
                <span className="text-rose-300 select-all">{incident.pom_tx_hash}</span>
              </div>
              <div>
                <span className="text-slate-500">Arbitrage Tx Hash: </span>
                <span className="text-emerald-300 select-all">{incident.arb_tx_hash}</span>
              </div>
              <div>
                <span className="text-slate-500">Target Pool Address: </span>
                <span className="text-slate-300 select-all">{incident.pom_details.pool_address}</span>
              </div>
              <div>
                <span className="text-slate-500">Manipulated Token Address: </span>
                <span className="text-slate-300 select-all">{incident.pom_token_address}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
