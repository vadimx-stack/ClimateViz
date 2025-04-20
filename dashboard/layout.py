import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta


def create_header():
    return html.Div(
        className="header",
        children=[
            html.Div(
                className="container header-content",
                children=[
                    html.Div([
                        html.H1("Climate", className="logo", children=[
                            "Climate", html.Span("Viz")
                        ]),
                        html.P("Аналитика климатических данных", className="app-title")
                    ]),
                ]
            )
        ]
    )


def create_intro_section():
    return html.Div(
        className="container",
        children=[
            html.Div(
                className="card",
                children=[
                    html.Div(
                        className="card-header",
                        children=[
                            html.H2("Добро пожаловать в платформу ClimateViz", className="card-title")
                        ]
                    ),
                    html.P(
                        "ClimateViz предоставляет интерактивный доступ к климатическим данным со всего мира. "
                        "Исследуйте тренды температуры, осадков и экстремальных погодных явлений с помощью интерактивных графиков и аналитики."
                    ),
                    html.P(
                        "Используйте фильтры ниже для выбора данных по интересующим вас критериям."
                    )
                ]
            )
        ]
    )


def create_filters_section():
    today = datetime.now()
    five_years_ago = today - timedelta(days=365 * 5)
    
    return html.Div(
        className="container",
        children=[
            html.Div(
                className="card",
                children=[
                    html.Div(
                        className="card-header",
                        children=[
                            html.H3("Фильтры данных", className="card-title")
                        ]
                    ),
                    html.Div(
                        className="filters-section",
                        children=[
                            html.Div(
                                className="filter-item",
                                children=[
                                    html.Label("Тип данных", className="filter-label"),
                                    dcc.Dropdown(
                                        id="data-type-dropdown",
                                        options=[
                                            {"label": "Температура", "value": "TAVG"},
                                            {"label": "Осадки", "value": "PRCP"},
                                            {"label": "Экстремальные явления", "value": "EXTREME"}
                                        ],
                                        value="TAVG",
                                        className="dropdown"
                                    )
                                ]
                            ),
                            html.Div(
                                className="filter-item",
                                children=[
                                    html.Label("Период", className="filter-label"),
                                    dcc.DatePickerRange(
                                        id="date-range",
                                        start_date=five_years_ago.date(),
                                        end_date=today.date(),
                                        className="date-picker"
                                    )
                                ]
                            ),
                            html.Div(
                                className="filter-item",
                                children=[
                                    html.Label("Анализ", className="filter-label"),
                                    dcc.Dropdown(
                                        id="analysis-type-dropdown",
                                        options=[
                                            {"label": "Сырые данные", "value": "raw"},
                                            {"label": "Скользящее среднее", "value": "moving_avg"},
                                            {"label": "Обнаружение аномалий", "value": "anomalies"},
                                            {"label": "Прогноз", "value": "forecast"}
                                        ],
                                        value="raw",
                                        className="dropdown"
                                    )
                                ]
                            ),
                            html.Div(
                                className="filter-item",
                                children=[
                                    html.Button(
                                        "Обновить", 
                                        id="update-button", 
                                        n_clicks=0
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )


def create_insights_section():
    return html.Div(
        className="container",
        children=[
            html.Div(
                className="card",
                children=[
                    html.Div(
                        className="card-header",
                        children=[
                            html.H3("Ключевые показатели", className="card-title")
                        ]
                    ),
                    html.Div(
                        id="data-insights",
                        className="data-insights",
                        children=[
                            html.Div(
                                className="insight-card",
                                children=[
                                    html.H4("Среднее значение", className="insight-title"),
                                    html.Div(id="avg-value", className="insight-value"),
                                    html.Div(id="avg-change", className="indicator")
                                ]
                            ),
                            html.Div(
                                className="insight-card",
                                children=[
                                    html.H4("Минимум", className="insight-title"),
                                    html.Div(id="min-value", className="insight-value"),
                                    html.Div(id="min-date", className="indicator")
                                ]
                            ),
                            html.Div(
                                className="insight-card",
                                children=[
                                    html.H4("Максимум", className="insight-title"),
                                    html.Div(id="max-value", className="insight-value"),
                                    html.Div(id="max-date", className="indicator")
                                ]
                            ),
                            html.Div(
                                className="insight-card",
                                children=[
                                    html.H4("Тренд", className="insight-title"),
                                    html.Div(id="trend-value", className="insight-value"),
                                    html.Div(id="trend-period", className="indicator")
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )


def create_visualization_section():
    return html.Div(
        className="container",
        children=[
            html.Div(
                className="card",
                children=[
                    html.Div(
                        className="card-header",
                        children=[
                            html.H3("Визуализация данных", className="card-title")
                        ]
                    ),
                    html.Div(
                        className="tabs-container",
                        children=[
                            dcc.Tabs(
                                id="visualization-tabs",
                                value="time-series",
                                children=[
                                    dcc.Tab(
                                        label="Временной ряд",
                                        value="time-series",
                                        className="tab",
                                        selected_className="tab-selected"
                                    ),
                                    dcc.Tab(
                                        label="Распределение",
                                        value="distribution",
                                        className="tab",
                                        selected_className="tab-selected"
                                    ),
                                    dcc.Tab(
                                        label="Сезонность",
                                        value="seasonality",
                                        className="tab",
                                        selected_className="tab-selected"
                                    ),
                                    dcc.Tab(
                                        label="Аномалии",
                                        value="anomalies",
                                        className="tab",
                                        selected_className="tab-selected"
                                    )
                                ]
                            ),
                            html.Div(
                                id="visualization-content",
                                className="chart-container",
                                children=[
                                    dcc.Loading(
                                        id="loading-visualization",
                                        type="default",
                                        children=[
                                            dcc.Graph(
                                                id="main-chart",
                                                config={"displayModeBar": True}
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )


def create_data_section():
    return html.Div(
        className="container",
        children=[
            html.Div(
                className="card",
                children=[
                    html.Div(
                        className="card-header",
                        children=[
                            html.H3("Данные", className="card-title")
                        ]
                    ),
                    html.Div(
                        id="data-table-container",
                        children=[
                            dcc.Loading(
                                id="loading-table",
                                type="default",
                                children=[
                                    dash.dash_table.DataTable(
                                        id="data-table",
                                        page_size=10,
                                        style_table={"overflowX": "auto"},
                                        style_cell={
                                            "textAlign": "left",
                                            "padding": "15px",
                                            "fontFamily": "Roboto, sans-serif"
                                        },
                                        style_header={
                                            "backgroundColor": "#f8f9fa",
                                            "fontWeight": "bold",
                                            "borderBottom": "1px solid #dee2e6"
                                        },
                                        style_data_conditional=[
                                            {
                                                "if": {"row_index": "odd"},
                                                "backgroundColor": "#f2f2f2"
                                            }
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )


def create_footer():
    return html.Footer(
        className="footer",
        children=[
            html.Div(
                className="container",
                children=[
                    html.P(f"ClimateViz © {datetime.now().year}. Все права защищены.")
                ]
            )
        ]
    )


def create_layout():
    return html.Div([
        create_header(),
        create_intro_section(),
        create_filters_section(),
        create_insights_section(),
        create_visualization_section(),
        create_data_section(),
        create_footer(),
        
        dcc.Store(id="data-store"),
        dcc.Store(id="processed-data-store")
    ]) 