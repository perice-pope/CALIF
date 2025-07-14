import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analytics.calculate_signals import calculate_signals


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Creates a sample DataFrame for testing signal calculations."""
    base_date = datetime.utcnow()
    dates = [base_date - timedelta(days=x) for x in range(35)]

    data = {
        'asset_type': (['watch'] * 35 + ['wine'] * 35),
        'ingestion_timestamp': dates * 2,
        'price': (
            list(np.linspace(100, 150, 30)) + [155, 160, 90, 95, 40] +
            list(np.linspace(500, 550, 30)) + [555, 560, 565, 570, 450]
        )
    }
    df = pd.DataFrame(data)
    df['ingestion_timestamp'] = pd.to_datetime(df['ingestion_timestamp'])
    df.sort_values(by=['asset_type', 'ingestion_timestamp'], inplace=True)
    return df

def test_calculate_signals_returns_dataframe(sample_data):
    """Test that the function returns a pandas DataFrame."""
    result = calculate_signals(sample_data)
    assert isinstance(result, pd.DataFrame)
    assert not result.empty

def test_calculate_signals_returns_latest_signal(sample_data):
    """Test that the function returns only the most recent signal per asset type."""
    result = calculate_signals(sample_data)
    assert len(result) == 2
    assert 'watch' in result['asset_type'].values
    assert 'wine' in result['asset_type'].values

def test_z_score_calculation(sample_data):
    """Test the z-score calculation for a known outlier."""
    result = calculate_signals(sample_data)
    watch_signal = result[result['asset_type'] == 'watch'].iloc[0]
    # The last price for 'watch' (80) is significantly lower than the mean.
    assert watch_signal['z_score'] < -1.6

def test_discount_signal_triggered(sample_data):
    """Test that the discount signal is triggered correctly."""
    result = calculate_signals(sample_data)
    watch_signal = result[result['asset_type'] == 'watch'].iloc[0]
    mean_price = watch_signal['rolling_mean_30d']
    current_price = watch_signal['price']

    assert current_price <= mean_price * 0.9
    assert watch_signal['discount_signal']

def test_is_deal_flag(sample_data):
    """Test that the is_deal flag is True when a signal is triggered."""
    result = calculate_signals(sample_data)
    watch_signal = result[result['asset_type'] == 'watch'].iloc[0]
    assert watch_signal['is_deal']

def test_no_deal_scenario():
    """Test a scenario where no deal should be flagged."""
    base_date = datetime.utcnow()
    dates = [base_date - timedelta(days=x) for x in range(35)]

    data = {
        'asset_type': ['watch'] * 35,
        'ingestion_timestamp': dates,
        'price': list(np.linspace(100, 110, 35)) # Stable prices
    }
    df = pd.DataFrame(data)
    df['ingestion_timestamp'] = pd.to_datetime(df['ingestion_timestamp'])
    df.sort_values(by='ingestion_timestamp', inplace=True)

    result = calculate_signals(df)
    watch_signal = result[result['asset_type'] == 'watch'].iloc[0]
    assert not watch_signal['is_deal']
    assert watch_signal['z_score'] > -2.0

def test_empty_dataframe():
    """Test that the function handles an empty DataFrame gracefully."""
    empty_df = pd.DataFrame(columns=['asset_type', 'ingestion_timestamp', 'price'])
    result = calculate_signals(empty_df)
    assert result.empty
    assert isinstance(result, pd.DataFrame)
