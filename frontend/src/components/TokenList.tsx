import React from 'react';
import { TokenInfo } from '../types';
import { Coins, ExternalLink, ShieldCheck } from 'lucide-react';

interface TokenListProps {
  tokens: TokenInfo[];
  sigma: number;
}

export const TokenList: React.FC<TokenListProps> = ({ tokens, sigma }) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-rose-500/10 text-rose-400 rounded-lg">
            <Coins className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              High-Value Token Registry & Total Supply Proxy (Section 3.3 & 4.2)
            </h3>
            <p className="text-xs text-slate-400">
              Only tokens with market cap ≥ $1,000,000 USD are evaluated (758 valuable tokens covering 99.96% of TVL).
            </p>
          </div>
        </div>
        <div className="text-xs font-mono text-rose-400 bg-rose-500/10 px-2.5 py-1 rounded-lg border border-rose-500/20">
          Active σ: {(sigma * 100).toFixed(4)}%
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/60 text-slate-400 font-semibold border-b border-slate-800">
            <tr>
              <th className="py-3 px-4">Asset</th>
              <th className="py-3 px-4">Contract Address</th>
              <th className="py-3 px-4 text-right">Unit Price</th>
              <th className="py-3 px-4 text-right">Circulating Total Supply sup(k)</th>
              <th className="py-3 px-4 text-right">Market Cap</th>
              <th className="py-3 px-4 text-right">POM Threshold Volume (σ × sup)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {tokens.map((t) => {
              const thresholdVol = t.total_supply * sigma;
              const thresholdUsd = thresholdVol * t.price_usd;
              return (
                <tr key={t.address} className="hover:bg-slate-800/30 transition">
                  <td className="py-3 px-4 font-sans">
                    <div className="flex items-center space-x-2">
                      <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-[10px] text-white">
                        {t.symbol.slice(0, 3)}
                      </div>
                      <div>
                        <div className="font-bold text-white text-xs">{t.symbol}</div>
                        <div className="text-[10px] text-slate-400">{t.name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-slate-400 truncate max-w-[160px]" title={t.address}>
                    {t.address}
                  </td>
                  <td className="py-3 px-4 text-right text-slate-300 font-semibold">
                    ${t.price_usd >= 1 ? t.price_usd.toLocaleString(undefined, { minimumFractionDigits: 2 }) : t.price_usd.toFixed(4)}
                  </td>
                  <td className="py-3 px-4 text-right text-slate-300">
                    {t.total_supply.toLocaleString()}
                  </td>
                  <td className="py-3 px-4 text-right text-emerald-400 font-semibold">
                    ${(t.market_cap_usd / 1_000_000).toFixed(1)}M
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="text-rose-400 font-bold">
                      ≥ {thresholdVol.toLocaleString(undefined, { maximumFractionDigits: 2 })} {t.symbol}
                    </div>
                    <div className="text-[10px] text-slate-500">
                      (~${thresholdUsd.toLocaleString(undefined, { maximumFractionDigits: 0 })})
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
