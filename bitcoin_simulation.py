import numpy as np
import pandas as pd

def simulate_bitcoin_price(days=60, s0=60000, mu=0.1, sigma=0.8):
    """
    Simulates Bitcoin price using Geometric Brownian Motion.
    """
    dt = 1/365  # Daily steps
    returns = np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.standard_normal(days))
    prices = s0 * np.cumprod(returns)
    # prepend the starting price
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

def run_trading_simulation(df, initial_balance=10000):
    """
    Implements a Golden Cross trading strategy and tracks performance.
    """
    balance = initial_balance
    btc_held = 0
    ledger = []

    print(f"{'Date':<12} | {'Price':>10} | {'MA7':>10} | {'MA30':>10} | {'Action':<10} | {'Balance':>10}")
    print("-" * 75)

    for i in range(len(df)):
        date = df.iloc[i]['Date'].strftime('%Y-%m-%d')
        price = df.iloc[i]['Price']
        ma7 = df.iloc[i]['MA7']
        ma30 = df.iloc[i]['MA30']

        action = "HOLD"

        # We need at least 30 days of data for the Golden Cross strategy
        if i > 0 and not np.isnan(ma30) and not np.isnan(df.iloc[i-1]['MA30']):
            prev_ma7 = df.iloc[i-1]['MA7']
            prev_ma30 = df.iloc[i-1]['MA30']

            # Golden Cross: MA7 crosses above MA30
            if prev_ma7 <= prev_ma30 and ma7 > ma30:
                if balance > 0:
                    btc_held = balance / price
                    balance = 0
                    action = "BUY"
                    ledger.append((date, action, price, btc_held, balance))

            # Death Cross: MA7 crosses below MA30
            elif prev_ma7 >= prev_ma30 and ma7 < ma30:
                if btc_held > 0:
                    balance = btc_held * price
                    btc_held = 0
                    action = "SELL"
                    ledger.append((date, action, price, btc_held, balance))

        print(f"{date:<12} | {price:10.2f} | {ma7:10.2f} | {ma30:10.2f} | {action:<10} | {balance + btc_held * price:10.2f}")

    final_portfolio_value = balance + btc_held * price
    total_return = ((final_portfolio_value - initial_balance) / initial_balance) * 100

    print("-" * 75)
    print(f"Initial Portfolio Value: ${initial_balance:,.2f}")
    print(f"Final Portfolio Value:   ${final_portfolio_value:,.2f}")
    print(f"Total Return:            {total_return:.2f}%")

    return ledger

if __name__ == "__main__":
    np.random.seed(42) # For reproducibility
    # Simulating more than 60 days to ensure we have enough data for 30-day MA
    # and still see 60 days of potential trading.
    # The prompt says "simulates 60 days of Bitcoin price data".
    # I will stick to 60 days, but note that the first 29 days won't have a 30-day MA.
    df = simulate_bitcoin_price(days=60)
    df = calculate_moving_averages(df)
    run_trading_simulation(df)
