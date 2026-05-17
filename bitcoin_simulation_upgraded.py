import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, List, Dict
from enum import Enum
import warnings

warnings.filterwarnings('ignore')


class TradeAction(Enum):
    """Enum for trade actions."""
    BUY = "BUY"
    SELL = "SELL"
    STOP_LOSS = "STOP_LOSS"
    HOLD = "HOLD"


@dataclass
class Trade:
    """Represents a single trade."""
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: pd.Timestamp
    exit_price: float
    action: str
    profit_loss: float
    profit_loss_pct: float
    btc_amount: float


@dataclass
class PortfolioMetrics:
    """Performance metrics for the portfolio."""
    initial_balance: float
    final_balance: float
    total_return_pct: float
    max_drawdown_pct: float
    win_rate_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win_pct: float
    avg_loss_pct: float
    profit_factor: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float


class BitcoinTradingSimulator:
    """Enhanced Bitcoin trading simulator with multiple strategies."""

    def __init__(self, initial_balance: float = 10000, fee_rate: float = 0.001):
        self.initial_balance = initial_balance
        self.fee_rate = fee_rate
        self.balance = initial_balance
        self.btc_held = 0
        self.trades: List[Trade] = []
        self.portfolio_values: List[float] = []
        self.ledger: List[Tuple] = []

    def simulate_price(self, days: int = 120, s0: float = 60000, 
                      mu: float = 0.1, sigma: float = 0.8,
                      start_date: str = '2023-01-01') -> pd.DataFrame:
        """
        Simulates Bitcoin price using Geometric Brownian Motion.
        
        Args:
            days: Number of simulation days
            s0: Initial price
            mu: Annual drift
            sigma: Annual volatility
            start_date: Starting date for simulation
        
        Returns:
            DataFrame with simulated prices
        """
        dt = 1 / 365
        returns = np.exp((mu - 0.5 * sigma**2) * dt + 
                        sigma * np.sqrt(dt) * np.random.standard_normal(days))
        prices = s0 * np.cumprod(returns)
        prices = np.insert(prices, 0, s0)

        dates = pd.date_range(start=start_date, periods=days + 1)
        df = pd.DataFrame({'Date': dates, 'Price': prices})
        return df

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates multiple technical indicators.
        
        Indicators:
        - Moving Averages (7, 30, 50, 200 days)
        - RSI (14-day)
        - MACD
        - Bollinger Bands
        - ATR (Average True Range)
        """
        # Moving Averages
        df['MA7'] = df['Price'].rolling(window=7).mean()
        df['MA30'] = df['Price'].rolling(window=30).mean()
        df['MA50'] = df['Price'].rolling(window=50).mean()
        df['MA200'] = df['Price'].rolling(window=200).mean()

        # RSI (14-day)
        df['RSI'] = self._calculate_rsi(df['Price'], period=14)

        # MACD
        df['EMA12'] = df['Price'].ewm(span=12).mean()
        df['EMA26'] = df['Price'].ewm(span=26).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal_Line'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']

        # Bollinger Bands
        bb = self._calculate_bollinger_bands(df['Price'], period=20, std_dev=2)
        df['BB_Upper'] = bb['upper']
        df['BB_Lower'] = bb['lower']
        df['BB_Middle'] = bb['middle']

        # ATR (14-day)
        df['ATR'] = self._calculate_atr(df, period=14)

        # Volume simulation (for reference)
        df['Volume'] = np.random.uniform(1e9, 5e9, len(df))

        return df

    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def _calculate_bollinger_bands(prices: pd.Series, period: int = 20, 
                                   std_dev: float = 2) -> Dict:
        """Calculate Bollinger Bands."""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        return {'upper': upper, 'middle': middle, 'lower': lower}

    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        df_temp = df.copy()
        df_temp['TR'] = np.maximum(
            df_temp['Price'].diff().abs(),
            np.maximum(
                (df_temp['Price'] - df_temp['Price'].shift()).abs(),
                (df_temp['Price'] - df_temp['Price'].shift()).abs()
            )
        )
        atr = df_temp['TR'].rolling(window=period).mean()
        return atr

    def run_golden_cross_strategy(self, df: pd.DataFrame, 
                                  stop_loss_pct: float = 0.05,
                                  take_profit_pct: float = 0.1) -> Tuple[List, List]:
        """
        Golden Cross strategy with enhanced risk management.
        
        Buy: When MA7 crosses above MA30
        Sell: When MA7 crosses below MA30 or take-profit/stop-loss triggered
        """
        self.balance = self.initial_balance
        self.btc_held = 0
        self.buy_price = 0
        self.trades = []
        self.portfolio_values = []
        self.ledger = []
        current_trade_start_balance = 0

        print(f"\n{'='*120}")
        print(f"{'GOLDEN CROSS STRATEGY':<60} | Fee Rate: {self.fee_rate*100:.2f}%")
        print(f"{'='*120}")
        print(f"{'Date':<12} | {'Price':>10} | {'MA7':>10} | {'MA30':>10} | {'RSI':>6} | {'Action':<12} | {'Portfolio':>12}")
        print("-" * 120)

        for i in range(len(df)):
            date = df.iloc[i]['Date']
            price = df.iloc[i]['Price']
            ma7 = df.iloc[i]['MA7']
            ma30 = df.iloc[i]['MA30']
            rsi = df.iloc[i]['RSI']

            action = TradeAction.HOLD

            if i > 0 and not np.isnan(ma30) and not np.isnan(df.iloc[i-1]['MA30']):
                prev_ma7 = df.iloc[i-1]['MA7']
                prev_ma30 = df.iloc[i-1]['MA30']

                # Golden Cross: BUY
                if prev_ma7 <= prev_ma30 and ma7 > ma30 and self.balance > 0:
                    current_trade_start_balance = self.balance
                    self.btc_held = (self.balance * (1 - self.fee_rate)) / price
                    self.balance = 0
                    self.buy_price = price
                    action = TradeAction.BUY
                    self.ledger.append((date, action.value, price))

                # Death Cross: SELL
                elif prev_ma7 >= prev_ma30 and ma7 < ma30 and self.btc_held > 0:
                    sell_price = price
                    self.balance = (self.btc_held * sell_price) * (1 - self.fee_rate)
                    
                    profit_loss = self.balance - current_trade_start_balance
                    profit_loss_pct = (profit_loss / current_trade_start_balance) * 100

                    self.trades.append(Trade(
                        entry_date=df.iloc[i]['Date'],
                        entry_price=self.buy_price,
                        exit_date=date,
                        exit_price=sell_price,
                        action="DEATH_CROSS",
                        profit_loss=profit_loss,
                        profit_loss_pct=profit_loss_pct,
                        btc_amount=self.btc_held
                    ))
                    
                    self.btc_held = 0
                    action = TradeAction.SELL
                    self.ledger.append((date, action.value, price))

                # Take Profit
                elif self.btc_held > 0 and price >= self.buy_price * (1 + take_profit_pct):
                    sell_price = price
                    self.balance = (self.btc_held * sell_price) * (1 - self.fee_rate)
                    
                    profit_loss = self.balance - current_trade_start_balance
                    profit_loss_pct = (profit_loss / current_trade_start_balance) * 100

                    self.trades.append(Trade(
                        entry_date=df.iloc[i]['Date'],
                        entry_price=self.buy_price,
                        exit_date=date,
                        exit_price=sell_price,
                        action="TAKE_PROFIT",
                        profit_loss=profit_loss,
                        profit_loss_pct=profit_loss_pct,
                        btc_amount=self.btc_held
                    ))
                    
                    self.btc_held = 0
                    action = TradeAction.SELL
                    self.ledger.append((date, action.value, price))

                # Stop Loss
                elif self.btc_held > 0 and price <= self.buy_price * (1 - stop_loss_pct):
                    sell_price = price
                    self.balance = (self.btc_held * sell_price) * (1 - self.fee_rate)
                    
                    profit_loss = self.balance - current_trade_start_balance
                    profit_loss_pct = (profit_loss / current_trade_start_balance) * 100

                    self.trades.append(Trade(
                        entry_date=df.iloc[i]['Date'],
                        entry_price=self.buy_price,
                        exit_date=date,
                        exit_price=sell_price,
                        action="STOP_LOSS",
                        profit_loss=profit_loss,
                        profit_loss_pct=profit_loss_pct,
                        btc_amount=self.btc_held
                    ))
                    
                    self.btc_held = 0
                    action = TradeAction.STOP_LOSS
                    self.ledger.append((date, action.value, price))

            current_value = self.balance + self.btc_held * price
            self.portfolio_values.append(current_value)
            
            date_str = date.strftime('%Y-%m-%d')
            rsi_str = f"{rsi:.1f}" if not np.isnan(rsi) else "N/A"
            print(f"{date_str:<12} | {price:10.2f} | {ma7:10.2f} | {ma30:10.2f} | {rsi_str:>6} | {action.value:<12} | {current_value:12.2f}")

        return self.ledger, self.portfolio_values

    def calculate_metrics(self, initial_balance: float) -> PortfolioMetrics:
        """Calculate comprehensive performance metrics."""
        final_value = self.balance + self.btc_held * (self.portfolio_values[-1] if self.portfolio_values else initial_balance)
        
        if not self.portfolio_values:
            return PortfolioMetrics(
                initial_balance=initial_balance,
                final_balance=final_value,
                total_return_pct=0,
                max_drawdown_pct=0,
                win_rate_pct=0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                avg_win_pct=0,
                avg_loss_pct=0,
                profit_factor=0,
                sharpe_ratio=0,
                sortino_ratio=0,
                calmar_ratio=0
            )

        total_return_pct = ((final_value - initial_balance) / initial_balance) * 100

        # Max Drawdown
        peak = self.portfolio_values[0]
        max_dd = 0
        for v in self.portfolio_values:
            if v > peak:
                peak = v
            dd = (peak - v) / peak
            if dd > max_dd:
                max_dd = dd

        # Win Rate
        winning_trades = sum(1 for trade in self.trades if trade.profit_loss > 0)
        losing_trades = len(self.trades) - winning_trades
        win_rate = (winning_trades / len(self.trades) * 100) if self.trades else 0

        # Average Win/Loss
        wins = [t.profit_loss_pct for t in self.trades if t.profit_loss > 0]
        losses = [t.profit_loss_pct for t in self.trades if t.profit_loss < 0]
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0

        # Profit Factor
        total_wins = sum(t.profit_loss for t in self.trades if t.profit_loss > 0)
        total_losses = abs(sum(t.profit_loss for t in self.trades if t.profit_loss < 0))
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # Sharpe Ratio (assuming risk-free rate = 0)
        returns = np.diff(self.portfolio_values) / np.array(self.portfolio_values[:-1])
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0

        # Sortino Ratio
        downside_returns = returns[returns < 0]
        sortino_ratio = np.mean(returns) / np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 and np.std(downside_returns) > 0 else 0

        # Calmar Ratio
        calmar_ratio = total_return_pct / (max_dd * 100) if max_dd > 0 else 0

        return PortfolioMetrics(
            initial_balance=initial_balance,
            final_balance=final_value,
            total_return_pct=total_return_pct,
            max_drawdown_pct=max_dd * 100,
            win_rate_pct=win_rate,
            total_trades=len(self.trades),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win_pct=avg_win,
            avg_loss_pct=avg_loss,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio
        )

    def print_metrics(self, metrics: PortfolioMetrics):
        """Print performance metrics."""
        print("\n" + "="*120)
        print("PERFORMANCE METRICS")
        print("="*120)
        print(f"Initial Portfolio Value:  ${metrics.initial_balance:,.2f}")
        print(f"Final Portfolio Value:    ${metrics.final_balance:,.2f}")
        print(f"Total Return:             {metrics.total_return_pct:.2f}%")
        print(f"Max Drawdown:             {metrics.max_drawdown_pct:.2f}%")
        print(f"\nTrade Statistics:")
        print(f"  Total Trades:           {metrics.total_trades}")
        print(f"  Winning Trades:         {metrics.winning_trades}")
        print(f"  Losing Trades:          {metrics.losing_trades}")
        print(f"  Win Rate:               {metrics.win_rate_pct:.2f}%")
        print(f"  Avg Win:                {metrics.avg_win_pct:.2f}%")
        print(f"  Avg Loss:               {metrics.avg_loss_pct:.2f}%")
        print(f"  Profit Factor:          {metrics.profit_factor:.2f}")
        print(f"\nRisk-Adjusted Metrics:")
        print(f"  Sharpe Ratio:           {metrics.sharpe_ratio:.4f}")
        print(f"  Sortino Ratio:          {metrics.sortino_ratio:.4f}")
        print(f"  Calmar Ratio:           {metrics.calmar_ratio:.4f}")
        print("="*120 + "\n")

    def plot_performance(self, df: pd.DataFrame, ledger: List, filename: str = 'trading_performance.png'):
        """
        Enhanced visualization with subplots.
        """
        fig, axes = plt.subplots(3, 1, figsize=(16, 12))

        # Plot 1: Price with Moving Averages
        ax1 = axes[0]
        ax1.plot(df['Date'], df['Price'], label='BTC Price', color='black', alpha=0.7, linewidth=2)
        ax1.plot(df['Date'], df['MA7'], label='7-day MA', color='blue', alpha=0.7)
        ax1.plot(df['Date'], df['MA30'], label='30-day MA', color='orange', alpha=0.7)
        ax1.plot(df['Date'], df['MA50'], label='50-day MA', color='green', alpha=0.5)
        ax1.fill_between(df['Date'], df['BB_Upper'], df['BB_Lower'], alpha=0.2, color='gray', label='Bollinger Bands')
        
        # Plot trade signals
        for date, action, price in ledger:
            if action == "BUY":
                ax1.scatter(date, price, color='green', marker='^', s=200, zorder=5, edgecolors='darkgreen', linewidth=2)
            elif action == "SELL":
                ax1.scatter(date, price, color='red', marker='v', s=200, zorder=5, edgecolors='darkred', linewidth=2)
            elif action == "STOP_LOSS":
                ax1.scatter(date, price, color='darkred', marker='X', s=200, zorder=5, edgecolors='black', linewidth=2)

        ax1.set_title('Bitcoin Golden Cross Strategy - Price & Moving Averages', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price (USD)', fontsize=12)
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)

        # Plot 2: RSI and MACD
        ax2 = axes[1]
        ax2.plot(df['Date'], df['RSI'], label='RSI (14)', color='purple', linewidth=2)
        ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought (70)')
        ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold (30)')
        ax2.fill_between(df['Date'], 30, 70, alpha=0.1, color='gray')
        ax2.set_ylabel('RSI', fontsize=12)
        ax2.set_title('Relative Strength Index (RSI)', fontsize=14, fontweight='bold')
        ax2.legend(loc='best', fontsize=10)
        ax2.grid(True, alpha=0.3)

        # Plot 3: Portfolio Value
        ax3 = axes[2]
        ax3.plot(df['Date'][:len(self.portfolio_values)], self.portfolio_values, 
                label='Portfolio Value', color='darkblue', linewidth=2)
        ax3.axhline(y=self.initial_balance, color='gray', linestyle='--', alpha=0.5, label='Initial Balance')
        ax3.fill_between(df['Date'][:len(self.portfolio_values)], self.portfolio_values, 
                         self.initial_balance, alpha=0.3, color='blue')
        ax3.set_ylabel('Portfolio Value (USD)', fontsize=12)
        ax3.set_xlabel('Date', fontsize=12)
        ax3.set_title('Portfolio Performance Over Time', fontsize=14, fontweight='bold')
        ax3.legend(loc='best', fontsize=10)
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✓ Plot saved as '{filename}' with high resolution (300 DPI)")
        plt.close()

    def generate_trade_report(self, filename: str = 'trade_report.csv'):
        """Generate detailed trade report."""
        if not self.trades:
            print("No trades executed.")
            return

        trade_data = []
        for trade in self.trades:
            trade_data.append({
                'Entry Date': trade.entry_date,
                'Entry Price': trade.entry_price,
                'Exit Date': trade.exit_date,
                'Exit Price': trade.exit_price,
                'Action': trade.action,
                'BTC Amount': trade.btc_amount,
                'Profit/Loss ($)': trade.profit_loss,
                'Profit/Loss (%)': trade.profit_loss_pct,
                'Hold Days': (trade.exit_date - trade.entry_date).days
            })

        report_df = pd.DataFrame(trade_data)
        report_df.to_csv(filename, index=False)
        print(f"✓ Trade report saved as '{filename}'")


def main():
    """Main simulation execution."""
    np.random.seed(42)

    # Initialize simulator
    simulator = BitcoinTradingSimulator(initial_balance=10000, fee_rate=0.001)

    # Generate price data
    print("Generating price data...")
    df = simulator.simulate_price(days=365, s0=60000, mu=0.15, sigma=0.6)

    # Calculate technical indicators
    print("Calculating technical indicators...")
    df = simulator.calculate_technical_indicators(df)

    # Run strategy
    print("Running Golden Cross strategy...")
    ledger, portfolio_values = simulator.run_golden_cross_strategy(
        df, 
        stop_loss_pct=0.05,
        take_profit_pct=0.10
    )

    # Calculate metrics
    metrics = simulator.calculate_metrics(simulator.initial_balance)
    simulator.print_metrics(metrics)

    # Generate visualizations and reports
    print("\nGenerating outputs...")
    simulator.plot_performance(df, ledger, 'trading_performance_upgraded.png')
    simulator.generate_trade_report('trade_report_detailed.csv')

    print("\n✓ Simulation completed successfully!")


if __name__ == "__main__":
    main()
