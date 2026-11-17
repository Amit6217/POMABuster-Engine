export type POMType = 'MARKET_DOMINATION' | 'WASH_SALE';

export interface TokenInfo {
  address: string;
  symbol: string;
  name: string;
  decimals: number;
  total_supply: number;
  price_usd: number;
  market_cap_usd: number;
  is_valuable: boolean;
}

export interface TransferLog {
  log_id?: string;
  tx_hash: string;
  block_number: number;
  log_index: number;
  sender: string;
  receiver: string;
  token_address: string;
  token_symbol: string;
  amount: number;
  timestamp: number;
}

export interface Trade {
  trade_id: string;
  tx_hash: string;
  block_number: number;
  operator: string;
  recipient: string;
  token_in: string;
  token_in_symbol: string;
  token_out: string;
  token_out_symbol: string;
  amount_in: number;
  amount_out: number;
  pool_address: string;
  timestamp: number;
  in_log_index: number;
  out_log_index: number;
}

export interface POMAIncident {
  incident_id: string;
  attack_type: POMType;
  is_multi_tx: boolean;
  block_distance: number;
  pom_tx_hash: string;
  pom_block: number;
  pom_operator: string;
  pom_token_address: string;
  pom_token_symbol: string;
  pom_amount: number;
  pom_supply_percentage: number;
  arb_tx_hash: string;
  arb_block: number;
  arb_operator: string;
  arb_profit_token: string;
  arb_profit_amount: number;
  arb_profit_usd: number;
  manipulated_tokens: string[];
  intermediate_tokens: string[];
  shared_tokens: string[];
  estimated_price_impact_pct: number;
  is_true_positive: boolean;
  flagged_timestamp: number;
  explanation: string;
  pom_details: {
    pom_type: string;
    pool_address: string;
    total_supply: number;
    threshold_sigma: number;
    trades_count: number;
  };
  arb_details: {
    trades_count: number;
    tokens_involved: string[];
    net_deltas: Record<string, number>;
  };
}

export interface DetectionStats {
  total_logs: number;
  total_trades: number;
  pom_candidates_found: number;
  market_domination_count: number;
  wash_sales_count: number;
  arbitrages_found: number;
  poma_incidents_total: number;
  multi_tx_incidents: number;
  single_tx_incidents: number;
  multi_tx_percentage: number;
  total_manipulated_volume_usd: number;
  total_extracted_profit_usd: number;
  worst_case_fpr: number;
  fnr: number;
  top_assets_targeted: Array<{ symbol: string; count: number; percentage: number }>;
  top_operators: Array<{ address: string; profit_usd: number }>;
  block_time_distribution: Record<string, number>;
}

export interface SystemConfig {
  sigma: number;
  block_window_n: number;
  strike_percentage: number;
  min_market_cap_usd: number;
  db_path: string;
}
