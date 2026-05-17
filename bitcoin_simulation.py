import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def simulate_bitcoin_price(days=60, s0=60000, mu=0.1, sigma=0.8):
    """
    Simulates Bitcoin price using Geometric Brownian Motion.
    """
    dt = 1/365  # Daily steps
    returns = np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.standard_normal(days))
    prices = s0 * np.cumprod(returns)
    prices = np.insert(prices, 0, s0)

    dates = pd.date_range(start='2023-01-01', periods=days+1)
    df = pd.DataFrame({'Date': dates, 'Price': prices})
    return df

def calculate_moving_averages(df):
    """
    Calculates 7-day and 30-day moving averages.
    """
    df['MA7'] = df['Price'].rolling(window=7).mean()
    df['MA30'] = df['Price'].rolling(window=30).mean()
    return df

def run_trading_simulation(df, initial_balance=10000, fee_rate=0.001):
    """
    Implements a Golden Cross trading strategy with fees and stop-loss.
    """
    balance = initial_balance
    btc_held = 0
    buy_price = 0
    stop_loss_pct = 0.05
    ledger = []
    portfolio_values = []

    trades = [] # Track (buy_value, sell_value) for win rate
    current_trade_start_balance = 0

    print(f"{'Date':<12} | {'Price':>10} | {'MA7':>10} | {'MA30':>10} | {'Action':<10} | {'Portfolio':>10}")
    print("-" * 85)

    for i in range(len(df)):
        date = df.iloc[i]['Date'].strftime('%Y-%m-%d')
        price = df.iloc[i]['Price']
        ma7 = df.iloc[i]['MA7']
        ma30 = df.iloc[i]['MA30']

        action = "HOLD"

        if i > 0 and not np.isnan(ma30) and not np.isnan(df.iloc[i-1]['MA30']):
            prev_ma7 = df.iloc[i-1]['MA7']
            prev_ma30 = df.iloc[i-1]['MA30']

            # Golden Cross: BUY
            if prev_ma7 <= prev_ma30 and ma7 > ma30 and balance > 0:
                current_trade_start_balance = balance
                btc_held = (balance * (1 - fee_rate)) / price
                balance = 0
                buy_price = price
                action = "BUY"
                ledger.append((df.iloc[i]['Date'], action, price))

            # Death Cross: SELL
            elif prev_ma7 >= prev_ma30 and ma7 < ma30 and btc_held > 0:
                balance = (btc_held * price) * (1 - fee_rate)
                trades.append((current_trade_start_balance, balance))
                btc_held = 0
                action = "SELL"
                ledger.append((df.iloc[i]['Date'], action, price))

            # Stop Loss
            elif btc_held > 0 and price <= buy_price * (1 - stop_loss_pct):
                balance = (btc_held * price) * (1 - fee_rate)
                trades.append((current_trade_start_balance, balance))
                btc_held = 0
                action = "STOP LOSS"
                ledger.append((df.iloc[i]['Date'], action, price))

        current_value = balance + btc_held * price
        portfolio_values.append(current_value)
        print(f"{date:<12} | {price:10.2f} | {ma7:10.2f} | {ma30:10.2f} | {action:<10} | {current_value:10.2f}")

    final_portfolio_value = balance + btc_held * price
    total_return = ((final_portfolio_value - initial_balance) / initial_balance) * 100

    # Max Drawdown
    peak = portfolio_values[0]
    max_dd = 0
    for v in portfolio_values:
        if v > peak: peak = v
        dd = (peak - v) / peak
        if dd > max_dd: max_dd = dd

    # Win Rate
    wins = sum(1 for start, end in trades if end > start)
    win_rate = (wins / len(trades) * 100) if trades else 0

    print("-" * 85)
    print(f"Initial Portfolio Value: ${initial_balance:,.2f}")
    print(f"Final Portfolio Value:   ${final_portfolio_value:,.2f}")
    print(f"Total Return:            {total_return:.2f}%")
    print(f"Max Drawdown:            {max_dd*100:.2f}%")
    print(f"Win Rate:                {win_rate:.2f}% ({len(trades)} completed trades)")

    return ledger, portfolio_values

def plot_performance(df, ledger):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Price'], label='BTC Price', color='gray', alpha=0.5)
    plt.plot(df['Date'], df['MA7'], label='7-day MA', color='blue')
    plt.plot(df['Date'], df['MA30'], label='30-day MA', color='orange')

    for date, action, price in ledger:
        if action == "BUY":
            plt.scatter(date, price, color='green', marker='^', s=100, label='BUY' if 'BUY' not in plt.gca().get_legend_handles_labels()[1] else "")
        elif action == "SELL":
            plt.scatter(date, price, color='red', marker='v', s=100, label='SELL' if 'SELL' not in plt.gca().get_legend_handles_labels()[1] else "")
        elif action == "STOP LOSS":
            plt.scatter(date, price, color='darkred', marker='X', s=100, label='STOP LOSS' if 'STOP LOSS' not in plt.gca().get_legend_handles_labels()[1] else "")

    plt.title('Bitcoin Golden Cross Strategy Performance')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.savefig('trading_performance.png')
    print("Plot saved as 'trading_performance.png'")

if __name__ == "__main__":
    np.random.seed(42)
    # Using 120 days to ensure we get some trades after the 30-day MA warmup
    df = simulate_bitcoin_price(days=120)
    df = calculate_moving_averages(df)
    ledger, portfolio_values = run_trading_simulation(df)
    plot_performance(df, ledger)
