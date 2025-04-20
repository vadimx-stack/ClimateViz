import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from climate_data import processor


def create_time_series_plot(df, analysis_type='raw', title=None, y_title=None):
    if df.empty:
        return empty_plot("Нет доступных данных")
    
    temp_df = df.copy()
    
    fig = go.Figure()
    
    if 'date' not in temp_df.columns or 'value' not in temp_df.columns:
        return empty_plot("Неверный формат данных")
    
    temp_df = temp_df.sort_values('date')
    
    if analysis_type == 'raw':
        fig.add_trace(go.Scatter(
            x=temp_df['date'],
            y=temp_df['value'],
            mode='lines',
            name='Значение',
            line=dict(color='#3498db', width=2)
        ))
    
    elif analysis_type == 'moving_avg':
        processed_df = processor.calculate_moving_average(temp_df)
        
        fig.add_trace(go.Scatter(
            x=processed_df['date'],
            y=processed_df['value'],
            mode='lines',
            name='Значение',
            line=dict(color='#3498db', width=1, dash='dot'),
            opacity=0.5
        ))
        
        fig.add_trace(go.Scatter(
            x=processed_df['date'],
            y=processed_df['moving_avg'],
            mode='lines',
            name='Скользящее среднее',
            line=dict(color='#e74c3c', width=2)
        ))
    
    elif analysis_type == 'anomalies':
        processed_df = processor.detect_anomalies(temp_df)
        
        fig.add_trace(go.Scatter(
            x=processed_df['date'],
            y=processed_df['value'],
            mode='lines',
            name='Значение',
            line=dict(color='#3498db', width=2)
        ))
        
        if 'is_anomaly' in processed_df.columns:
            anomalies_df = processed_df[processed_df['is_anomaly']]
            
            if not anomalies_df.empty:
                fig.add_trace(go.Scatter(
                    x=anomalies_df['date'],
                    y=anomalies_df['value'],
                    mode='markers',
                    name='Аномалии',
                    marker=dict(color='#e74c3c', size=10, symbol='circle')
                ))
    
    elif analysis_type == 'forecast':
        forecast_days = 30
        forecast_df = processor.forecast_simple(temp_df, forecast_days=forecast_days)
        
        fig.add_trace(go.Scatter(
            x=temp_df['date'],
            y=temp_df['value'],
            mode='lines',
            name='Исторические данные',
            line=dict(color='#3498db', width=2)
        ))
        
        if not forecast_df.empty:
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['value'],
                mode='lines',
                name='Прогноз',
                line=dict(color='#e74c3c', width=2, dash='dot')
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=[y * 1.1 for y in forecast_df['value']],
                mode='lines',
                name='Верхняя граница',
                line=dict(color='#e74c3c', width=1, dash='dot'),
                opacity=0.3
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=[y * 0.9 for y in forecast_df['value']],
                mode='lines',
                name='Нижняя граница',
                line=dict(color='#e74c3c', width=1, dash='dot'),
                opacity=0.3,
                fill='tonexty'
            ))
    
    plot_title = title if title else "Временной ряд"
    y_axis_title = y_title if y_title else "Значение"
    
    fig.update_layout(
        title=plot_title,
        xaxis_title="Дата",
        yaxis_title=y_axis_title,
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def create_distribution_plot(df, title=None):
    if df.empty:
        return empty_plot("Нет доступных данных")
    
    temp_df = df.copy()
    
    if 'value' not in temp_df.columns:
        return empty_plot("Неверный формат данных")
    
    values = temp_df['value'].dropna()
    
    if len(values) == 0:
        return empty_plot("Нет доступных данных")
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=values,
        nbinsx=30,
        marker_color='#3498db',
        opacity=0.7,
        name="Распределение"
    ))
    
    fig.add_trace(go.Violin(
        x=values,
        box_visible=True,
        line_color='#e74c3c',
        meanline_visible=True,
        fillcolor='#e74c3c',
        opacity=0.5,
        name="Плотность",
        side='positive',
        orientation='h',
        xaxis='x2',
        points=False
    ))
    
    plot_title = title if title else "Распределение значений"
    
    fig.update_layout(
        title=plot_title,
        xaxis_title="Значение",
        yaxis_title="Частота",
        template="plotly_white",
        xaxis2=dict(
            overlaying='x',
            side='top',
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def create_seasonality_plot(df, title=None):
    if df.empty:
        return empty_plot("Нет доступных данных")
    
    temp_df = df.copy()
    
    if 'date' not in temp_df.columns or 'value' not in temp_df.columns:
        return empty_plot("Неверный формат данных")
    
    temp_df['month'] = temp_df['date'].dt.month
    temp_df['year'] = temp_df['date'].dt.year
    
    monthly_data = temp_df.groupby(['year', 'month'])['value'].mean().reset_index()
    
    months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
    monthly_data['month_name'] = monthly_data['month'].apply(lambda x: months[x-1])
    
    years = monthly_data['year'].unique()
    
    fig = go.Figure()
    
    for year in years:
        year_data = monthly_data[monthly_data['year'] == year]
        
        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data['value'],
            mode='lines+markers',
            name=str(year),
            hovertemplate='%{y:.2f}'
        ))
    
    fig.update_xaxes(
        tickvals=list(range(1, 13)),
        ticktext=months
    )
    
    plot_title = title if title else "Сезонность по годам"
    
    fig.update_layout(
        title=plot_title,
        xaxis_title="Месяц",
        yaxis_title="Значение",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def create_anomalies_plot(df, title=None):
    if df.empty:
        return empty_plot("Нет доступных данных")
    
    temp_df = df.copy()
    
    if 'date' not in temp_df.columns or 'value' not in temp_df.columns:
        return empty_plot("Неверный формат данных")
    
    processed_df = processor.detect_anomalies(temp_df)
    
    fig = go.Figure()
    
    if 'z_score' in processed_df.columns:
        fig.add_trace(go.Scatter(
            x=processed_df['date'],
            y=processed_df['z_score'],
            mode='lines',
            name='Z-показатель',
            line=dict(color='#3498db', width=2)
        ))
        
        fig.add_shape(
            type="line",
            x0=processed_df['date'].min(),
            y0=2,
            x1=processed_df['date'].max(),
            y1=2,
            line=dict(
                color="#e74c3c",
                width=2,
                dash="dash",
            )
        )
        
        fig.add_shape(
            type="line",
            x0=processed_df['date'].min(),
            y0=-2,
            x1=processed_df['date'].max(),
            y1=-2,
            line=dict(
                color="#e74c3c",
                width=2,
                dash="dash",
            )
        )
        
        if 'is_anomaly' in processed_df.columns:
            anomalies_df = processed_df[processed_df['is_anomaly']]
            
            if not anomalies_df.empty:
                fig.add_trace(go.Scatter(
                    x=anomalies_df['date'],
                    y=anomalies_df['z_score'],
                    mode='markers',
                    name='Аномалии',
                    marker=dict(color='#e74c3c', size=10, symbol='circle')
                ))
    
    plot_title = title if title else "Обнаружение аномалий (Z-показатель)"
    
    fig.update_layout(
        title=plot_title,
        xaxis_title="Дата",
        yaxis_title="Z-показатель",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def empty_plot(message="Нет данных для отображения"):
    fig = go.Figure()
    
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text=message,
        showarrow=False,
        font=dict(size=16)
    )
    
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    return fig 