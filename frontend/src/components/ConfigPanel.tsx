import React, { useState } from 'react';
import { Sliders, HelpCircle, AlertTriangle, Check, ArrowRight } from 'lucide-react';
import { SystemConfig } from '../types';

interface ConfigPanelProps {
  config: SystemConfig;
  onApplyConfig: (newSigma: number, newN: number, newStrike: number) => void;
  isScanning: boolean;
}

export const ConfigPanel: React.FC<ConfigPanelProps> = ({ config, onApplyConfig, isScanning }) => {
  const [sigmaPct, setSigmaPct] = useState<number>(config.sigma * 100);
  const [blockWindowN, setBlockWindowN] = useState<number>(config.block_window_n);
  const [strikePct, setStrikePct] = useState<number>(config.strike_percentage * 100);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onApplyConfig(sigmaPct / 100.0, blockWindowN, strikePct / 100.0);
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-rose-500/10 text-rose-400 rounded-lg">
            <Sliders className="w-4 h-4" />
          </div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Detection Thresholds & Model Parameters
          </h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          Paper Optimal: σ = 0.010%, n = 2 blocks
        </span>
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 1. Sigma: Total Supply Percentage */}
        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs">
            <label className="font-semibold text-slate-300 flex items-center space-x-1">
              <span>Token Total Supply Threshold (σ)</span>
            </label>
            <span className="font-mono text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded">
              {sigmaPct.toFixed(3)}%
            </span>
          </div>
          <input
            type="range"
            min="0.001"
            max="0.05"
            step="0.001"
            value={sigmaPct}
            onChange={(e) => setSigmaPct(parseFloat(e.target.value))}
            className="w-full h-2 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-rose-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>0.001% (Aggressive)</span>
            <span>0.010% (Optimal)</span>
            <span>0.050% (Conservative)</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Trades exceeding <span className="text-slate-200">σ × sup(token)</span> are flagged as Market Domination or Wash Sale.
          </p>
        </div>

        {/* 2. Block Window n */}
        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs">
            <label className="font-semibold text-slate-300">
              Block Window (n)
            </label>
            <span className="font-mono text-cyan-400 font-bold bg-cyan-500/10 px-2 py-0.5 rounded">
              {blockWindowN === -1 ? 'Single-Tx (-1)' : `${blockWindowN} Block${blockWindowN === 1 ? '' : 's'}`}
            </span>
          </div>
          <div className="grid grid-cols-4 gap-1.5">
            {[
              { val: -1, label: '-1 (Single)' },
              { val: 0, label: '0 (Bundle)' },
              { val: 2, label: '2 (Optimal)' },
              { val: 5, label: '5 (Wide)' },
            ].map((opt) => (
              <button
                type="button"
                key={opt.val}
                onClick={() => setBlockWindowN(opt.val)}
                className={`py-1.5 px-2 text-xs font-mono rounded-lg border transition ${
                  blockWindowN === opt.val
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 font-bold'
                    : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
          <p className="text-[11px] text-slate-400">
            {blockWindowN === -1 ? (
              <span className="text-amber-400 flex items-center space-x-1">
                <AlertTriangle className="w-3 h-3 shrink-0" />
                <span>DeFiRanger mode: misses multi-tx attacks (&gt;74% FNR)</span>
              </span>
            ) : (
              <span>Captures multi-tx Flashbots bundles across up to {blockWindowN} blocks (98.7% of POMAs).</span>
            )}
          </p>
        </div>

        {/* 3. Strike Percentage & Apply Button */}
        <div className="space-y-2 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center text-xs mb-2">
              <label className="font-semibold text-slate-300">
                Strike Impact Watermark
              </label>
              <span className="font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded">
                {strikePct.toFixed(1)}%
              </span>
            </div>
            <input
              type="range"
              min="0.5"
              max="5.0"
              step="0.5"
              value={strikePct}
              onChange={(e) => setStrikePct(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <p className="text-[11px] text-slate-400 mt-1">
              Used in Section 4.6 for False Positive verification (2.0% industry standard).
            </p>
          </div>

          <button
            type="submit"
            disabled={isScanning}
            className="w-full py-2 px-4 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-xl shadow-md shadow-rose-600/20 transition flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            <span>{isScanning ? 'Re-scanning Dataset...' : 'Apply Thresholds & Re-Analyze'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </form>
    </div>
  );
};
