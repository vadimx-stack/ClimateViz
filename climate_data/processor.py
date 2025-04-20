import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calculate_moving_average(df, window_size=12):
    if df.empty:
        return pd.DataFrame()
    
    temp_df = df.copy()
    if 'date' in temp_df.columns and 'value' in temp_df.columns:
        temp_df = temp_df.sort_values('date')
        temp_df['moving_avg'] = temp_df['value'].rolling(window=window_size).mean()
    
    return temp_df


def normalize_data(df, column='value'):
    if df.empty or column not in df.columns:
        return df
    
    temp_df = df.copy()
    min_val = temp_df[column].min()
    max_val = temp_df[column].max()
    
    if max_val > min_val:
        temp_df[f'{column}_normalized'] = (temp_df[column] - min_val) / (max_val - min_val)
    else:
        temp_df[f'{column}_normalized'] = 0
    
    return temp_df


def detect_anomalies(df, column='value', threshold=2):
    if df.empty or column not in df.columns:
        return df
    
    temp_df = df.copy()
    mean_val = temp_df[column].mean()
    std_val = temp_df[column].std()
    
    if std_val > 0:
        temp_df['z_score'] = (temp_df[column] - mean_val) / std_val
        temp_df['is_anomaly'] = abs(temp_df['z_score']) > threshold
    else:
        temp_df['z_score'] = 0
        temp_df['is_anomaly'] = False
    
    return temp_df


def compute_trends(df, column='value', periods=None):
    if df.empty or column not in df.columns or 'date' not in df.columns:
        return None
    
    temp_df = df.copy().sort_values('date')
    
    if periods is None:
        periods = {
            'yearly': 365,
            'monthly': 30,
            'weekly': 7
        }
    
    result = {}
    
    for period_name, days in periods.items():
        period_df = temp_df.copy()
        period_df['period'] = period_df['date'].dt.to_period('Y' if period_name == 'yearly' else 'M' if period_name == 'monthly' else 'W')
        period_stats = period_df.groupby('period')[column].agg(['mean', 'std', 'min', 'max'])
        
        period_change = None
        if len(period_stats) > 1:
            first_period = period_stats.iloc[0]['mean']
            last_period = period_stats.iloc[-1]['mean']
            period_change = ((last_period - first_period) / first_period) * 100 if first_period != 0 else np.nan
        
        result[period_name] = {
            'stats': period_stats,
            'change_percent': period_change
        }
    
    return result


def forecast_simple(df, column='value', forecast_days=30):
    if df.empty or column not in df.columns or 'date' not in df.columns:
        return pd.DataFrame()
    
    temp_df = df.copy().sort_values('date')
    
    if len(temp_df) < 2:
        return pd.DataFrame()
    
    last_date = temp_df['date'].max()
    
    x = np.arange(len(temp_df))
    y = temp_df[column].values
    
    coeffs = np.polyfit(x, y, 1)
    poly = np.poly1d(coeffs)
    
    future_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
    future_x = np.arange(len(temp_df), len(temp_df) + forecast_days)
    future_y = poly(future_x)
    
    forecast_df = pd.DataFrame({
        'date': future_dates,
        column: future_y,
        'type': f'{column}_forecast'
    })
    
    return forecast_df


def aggregate_by_type(df):
    if df.empty or 'type' not in df.columns:
        return {}
    
    result = {}
    types = df['type'].unique()
    
    for data_type in types:
        type_df = df[df['type'] == data_type].copy()
        result[data_type] = type_df
    
    return result 