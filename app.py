import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from flask import Flask, render_template, redirect, url_for
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os
from pathlib import Path

from climate_data import api, processor
from dashboard import layout, visualizations

server = Flask(__name__)

app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/dash/',
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    assets_folder=str(Path(__file__).parent / "dashboard" / "assets")
)

app.layout = layout.create_layout()


@server.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}


@server.route('/')
def index():
    return render_template('base.html')


@server.route('/dashboard')
def dashboard():
    return redirect('/dash/')


@server.route('/about')
def about():
    return render_template('base.html')


@app.callback(
    Output('data-store', 'data'),
    Input('update-button', 'n_clicks'),
    State('data-type-dropdown', 'value'),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
    prevent_initial_call=True
)
def load_data(n_clicks, data_type, start_date, end_date):
    if n_clicks is None:
        raise PreventUpdate
    
    if start_date is None or end_date is None:
        start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    data = api.get_sample_data()
    
    if data_type:
        data = data[data['type'] == data_type]
    
    data_json = data.to_json(orient='split', date_format='iso')
    return data_json


@app.callback(
    Output('processed-data-store', 'data'),
    Input('data-store', 'data'),
    Input('analysis-type-dropdown', 'value'),
    prevent_initial_call=True
)
def process_data(data_json, analysis_type):
    if data_json is None:
        raise PreventUpdate
    
    data = pd.read_json(data_json, orient='split')
    
    if analysis_type == 'moving_avg':
        processed_data = processor.calculate_moving_average(data)
    elif analysis_type == 'anomalies':
        processed_data = processor.detect_anomalies(data)
    else:
        processed_data = data
    
    return processed_data.to_json(orient='split', date_format='iso')


@app.callback(
    Output('main-chart', 'figure'),
    Input('processed-data-store', 'data'),
    Input('visualization-tabs', 'value'),
    Input('analysis-type-dropdown', 'value'),
    Input('data-type-dropdown', 'value'),
    prevent_initial_call=True
)
def update_visualization(data_json, tab_value, analysis_type, data_type):
    if data_json is None:
        return visualizations.empty_plot()
    
    data = pd.read_json(data_json, orient='split')
    
    if data.empty:
        return visualizations.empty_plot()
    
    titles = {
        'TAVG': 'Температура',
        'PRCP': 'Осадки',
        'EXTREME': 'Экстремальные явления'
    }
    
    y_titles = {
        'TAVG': 'Температура (°C)',
        'PRCP': 'Количество осадков (мм)',
        'EXTREME': 'Интенсивность явления'
    }
    
    title = titles.get(data_type, "Данные")
    y_title = y_titles.get(data_type, "Значение")
    
    if tab_value == 'time-series':
        return visualizations.create_time_series_plot(
            data, 
            analysis_type=analysis_type,
            title=f"{title} - Временной ряд",
            y_title=y_title
        )
    elif tab_value == 'distribution':
        return visualizations.create_distribution_plot(
            data,
            title=f"{title} - Распределение значений"
        )
    elif tab_value == 'seasonality':
        return visualizations.create_seasonality_plot(
            data,
            title=f"{title} - Сезонность"
        )
    elif tab_value == 'anomalies':
        return visualizations.create_anomalies_plot(
            data,
            title=f"{title} - Аномалии"
        )
    else:
        return visualizations.empty_plot()


@app.callback(
    [
        Output('avg-value', 'children'),
        Output('min-value', 'children'),
        Output('max-value', 'children'),
        Output('trend-value', 'children'),
        Output('avg-change', 'children'),
        Output('min-date', 'children'),
        Output('max-date', 'children'),
        Output('trend-period', 'children'),
        Output('avg-change', 'className'),
        Output('data-table', 'data'),
        Output('data-table', 'columns')
    ],
    Input('processed-data-store', 'data'),
    prevent_initial_call=True
)
def update_insights(data_json):
    if data_json is None:
        empty_insight = "—"
        return empty_insight, empty_insight, empty_insight, empty_insight, "", "", "", "", "indicator", [], []
    
    data = pd.read_json(data_json, orient='split')
    
    if data.empty or 'value' not in data.columns:
        empty_insight = "—"
        return empty_insight, empty_insight, empty_insight, empty_insight, "", "", "", "", "indicator", [], []
    
    avg_value = f"{data['value'].mean():.2f}"
    
    min_value = f"{data['value'].min():.2f}"
    min_date = ""
    if 'date' in data.columns:
        min_idx = data['value'].idxmin()
        min_date = f"({data.loc[min_idx, 'date'].strftime('%d.%m.%Y')})"
    
    max_value = f"{data['value'].max():.2f}"
    max_date = ""
    if 'date' in data.columns:
        max_idx = data['value'].idxmax()
        max_date = f"({data.loc[max_idx, 'date'].strftime('%d.%m.%Y')})"
    
    trends = None
    if 'date' in data.columns and len(data) > 1:
        trends = processor.compute_trends(data)
    
    trend_value = "—"
    trend_period = ""
    avg_change = ""
    change_class = "indicator"
    
    if trends and 'yearly' in trends:
        yearly_change = trends['yearly']['change_percent']
        if yearly_change is not None and not np.isnan(yearly_change):
            sign = "+" if yearly_change > 0 else ""
            trend_value = f"{sign}{yearly_change:.2f}%"
            trend_period = "в год"
            
            sign_text = "+" if yearly_change > 0 else ""
            avg_change = f"{sign_text}{yearly_change:.2f}% (годовой)"
            change_class = "indicator positive-change" if yearly_change > 0 else "indicator negative-change"
    
    table_data = []
    if not data.empty and 'date' in data.columns:
        table_df = data.copy()
        table_df['date'] = table_df['date'].dt.strftime('%d.%m.%Y')
        table_data = table_df.to_dict('records')
    
    columns = [{"name": col.capitalize(), "id": col} for col in data.columns if col not in ['z_score', 'is_anomaly']]
    
    return avg_value, min_value, max_value, trend_value, avg_change, min_date, max_date, trend_period, change_class, table_data, columns


if __name__ == '__main__':
    server.run(debug=True, port=8050) 