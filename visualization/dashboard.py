import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 导入自定义模块
from analysis.data_analyzer import WeatherDataAnalyzer
from visualization.charts import WeatherCharts

# 初始化Dash应用
app = dash.Dash(__name__, title='气象数据分析与可视化系统', suppress_callback_exceptions=True)
server = app.server

# 初始化分析器和图表生成器
analyzer = WeatherDataAnalyzer()
charts = WeatherCharts()

# 城市列表
CITIES = ['beijing', 'shanghai', 'guangzhou', 'shenzhen', 'chengdu']

# 指标列表
METRICS = [
    {'value': 'temperature', 'label': '温度 (°C)'},
    {'value': 'pressure', 'label': '气压 (hPa)'},
    {'value': 'humidity', 'label': '湿度 (%)'},
    {'value': 'precipitation', 'label': '降水量 (mm)'},
    {'value': 'wind_speed', 'label': '风速 (m/s)'},
    {'value': 'wind_direction', 'label': '风向 (°)'}
]

METRIC_LABELS = {metric['value']: metric['label'] for metric in METRICS}

# 时间周期列表
TIME_PERIODS = [
    {'value': 'daily', 'label': '日'},
    {'value': 'monthly', 'label': '月'},
    {'value': 'seasonal', 'label': '季节'}
]

# 图表类型列表
CHART_TYPES = [
    {'value': 'line', 'label': '折线图'},
    {'value': 'bar', 'label': '柱状图'},
    {'value': 'heatmap', 'label': '热力图'},
    {'value': 'radar', 'label': '雷达图'},
    {'value': 'scatter', 'label': '散点图'},
    {'value': 'box', 'label': '箱线图'},
    {'value': 'histogram', 'label': '直方图'}
]

# ------------------------------
# 应用布局
# ------------------------------

app.layout = html.Div(style={'backgroundColor': '#f5f5f5', 'minHeight': '100vh'}, children=[
    # 标题栏
    html.Div(style={'backgroundColor': '#1e3a8a', 'color': 'white', 'padding': '1rem', 'textAlign': 'center'}, children=[
        html.H1(children='气象数据分析与可视化系统', style={'margin': 0}),
        html.P(children='多维度数据分析 · 极端事件识别 · 短期气象预测', style={'margin': '0.5rem 0 0 0'})
    ]),
    
    # 导航栏
    html.Div(style={'backgroundColor': '#3b82f6', 'color': 'white', 'padding': '0.5rem', 'textAlign': 'center'}, children=[
        dcc.Tabs(id='tabs', value='analysis', style={'color': 'white'}, children=[
            dcc.Tab(label='多维度数据分析', value='analysis', style={'color': 'white'}),
            dcc.Tab(label='极端事件识别', value='extreme_events', style={'color': 'white'}),
            dcc.Tab(label='短期气象预测', value='forecast', style={'color': 'white'}),
            dcc.Tab(label='智能预警', value='alert', style={'color': 'white'})
        ])
    ]),
    
    # 主内容区
    html.Div(style={'padding': '1rem'}, children=[
        # 多维度数据分析标签页
        html.Div(id='analysis-tab', children=[
            # 筛选条件
            html.Div(style={'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '1rem'}, children=[
                html.H3(children='筛选条件', style={'marginTop': 0}),
                html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '1rem', 'alignItems': 'flex-start'}, children=[
                    # 城市选择
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('城市:'),
                        dcc.Dropdown(
                            id='city-select',
                            options=[{'label': city.capitalize(), 'value': city} for city in CITIES],
                            value='beijing',
                            multi=True
                        )
                    ]),
                    
                    # 指标选择
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('指标:'),
                        dcc.Dropdown(
                            id='metric-select',
                            options=METRICS,
                            value='temperature'
                        )
                    ]),
                    
                    # 时间周期选择
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('时间周期:'),
                        dcc.Dropdown(
                            id='time-period-select',
                            options=TIME_PERIODS,
                            value='daily'
                        )
                    ]),
                    
                    # 图表类型选择
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('图表类型:'),
                        dcc.Dropdown(
                            id='chart-type-select',
                            options=CHART_TYPES,
                            value='line'
                        )
                    ]),
                    
                    # 开始日期选择
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('开始日期:'),
                        dcc.DatePickerSingle(
                            id='start-date',
                            date=datetime.now() - timedelta(days=30),
                            display_format='YYYY-MM-DD'
                        )
                    ]),
                    
                    # 结束日期选择
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('结束日期:'),
                        dcc.DatePickerSingle(
                            id='end-date',
                            date=datetime.now(),
                            display_format='YYYY-MM-DD'
                        )
                    ]),
                    
                    # 查询按钮
                    html.Div(style={'flex': '0 0 auto', 'display': 'flex', 'alignItems': 'flex-end'}, children=[
                        html.Button('查询', id='query-button', n_clicks=0, style={
                            'backgroundColor': '#10b981',
                            'color': 'white',
                            'border': 'none',
                            'padding': '0.5rem 1rem',
                            'borderRadius': '4px',
                            'cursor': 'pointer'
                        })
                    ]),
                    
                    # 导出按钮
                    html.Div(style={'flex': '0 0 auto', 'display': 'flex', 'alignItems': 'flex-end'}, children=[
                        html.Button('导出图表', id='export-button', n_clicks=0, style={
                            'backgroundColor': '#6366f1',
                            'color': 'white',
                            'border': 'none',
                            'padding': '0.5rem 1rem',
                            'borderRadius': '4px',
                            'cursor': 'pointer',
                            'marginLeft': '0.5rem'
                        })
                    ]),
                ])
            ]),
            
            # 图表区域
            html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '1rem', 'marginBottom': '1rem'}, children=[
                # 主要图表
                html.Div(style={'flex': '2 1 600px', 'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                    html.H3(children='主要图表', style={'marginTop': 0}),
                    dcc.Graph(id='main-chart', figure=go.Figure(), style={'height': '400px'})
                ]),
                
                # 相关性热力图
                html.Div(style={'flex': '1 1 400px', 'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                    html.H3(children='指标相关性热力图', style={'marginTop': 0}),
                    dcc.Graph(id='correlation-heatmap', figure=go.Figure(), style={'height': '400px'})
                ])
            ]),
            
            # 辅助图表区域
            html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '1rem'}, children=[
                # 指标分布箱线图
                html.Div(style={'flex': '1 1 400px', 'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                    html.H3(children='指标分布箱线图', style={'marginTop': 0}),
                    dcc.Graph(id='box-plot', figure=go.Figure(), style={'height': '300px'})
                ]),
                
                # 指标分布直方图
                html.Div(style={'flex': '1 1 400px', 'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                    html.H3(children='指标分布直方图', style={'marginTop': 0}),
                    dcc.Graph(id='histogram', figure=go.Figure(), style={'height': '300px'})
                ])
            ])
        ]),
        
        # 极端事件识别标签页
        html.Div(id='extreme-events-tab', style={'display': 'none'}, children=[
            # 筛选条件
            html.Div(style={'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '1rem'}, children=[
                html.H3(children='筛选条件', style={'marginTop': 0}),
                html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '1rem', 'alignItems': 'flex-start'}, children=[
                    # 城市选择
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('城市:'),
                        dcc.Dropdown(
                            id='extreme-city-select',
                            options=[{'label': city.capitalize(), 'value': city} for city in CITIES],
                            value='beijing',
                            multi=True
                        )
                    ]),
                    
                    # 开始日期选择
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('开始日期:'),
                        dcc.DatePickerSingle(
                            id='extreme-start-date',
                            date=datetime.now() - timedelta(days=60),
                            display_format='YYYY-MM-DD'
                        )
                    ]),
                    
                    # 结束日期选择
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('结束日期:'),
                        dcc.DatePickerSingle(
                            id='extreme-end-date',
                            date=datetime.now(),
                            display_format='YYYY-MM-DD'
                        )
                    ]),
                    
                    # 查询按钮
                    html.Div(style={'flex': '0 0 auto', 'display': 'flex', 'alignItems': 'flex-end'}, children=[
                        html.Button('查询', id='extreme-query-button', n_clicks=0, style={
                            'backgroundColor': '#10b981',
                            'color': 'white',
                            'border': 'none',
                            'padding': '0.5rem 1rem',
                            'borderRadius': '4px',
                            'cursor': 'pointer'
                        })
                    ])
                ])
            ]),
            
            # 图表区域
            html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '1rem', 'marginBottom': '1rem'}, children=[
                # 极端事件分布
                html.Div(style={'flex': '1 1 500px', 'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                    html.H3(children='极端事件分布', style={'marginTop': 0}),
                    dcc.Graph(id='extreme-events-chart', figure=go.Figure(), style={'height': '400px'})
                ]),
                
                # 极端事件时间线
                html.Div(style={'flex': '2 1 600px', 'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                    html.H3(children='极端事件时间线', style={'marginTop': 0}),
                    dcc.Graph(id='extreme-events-timeline', figure=go.Figure(), style={'height': '400px'})
                ])
            ]),
            
            # 极端事件详情
            html.Div(style={'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                html.H3(children='极端事件详情', style={'marginTop': 0}),
                html.Div(id='extreme-events-table', children=html.P('请先查询极端事件'))
            ])
        ]),
        
        # 短期气象预测标签页
        html.Div(id='forecast-tab', style={'display': 'none'}, children=[
            # 筛选条件
            html.Div(style={'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '1rem'}, children=[
                html.H3(children='预测参数', style={'marginTop': 0}),
                html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '1rem', 'alignItems': 'flex-start'}, children=[
                    # 城市选择
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('城市:'),
                        dcc.Dropdown(
                            id='forecast-city-select',
                            options=[{'label': city.capitalize(), 'value': city} for city in CITIES],
                            value='beijing'
                        )
                    ]),
                    
                    # 指标选择
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('指标:'),
                        dcc.Dropdown(
                            id='forecast-metric-select',
                            options=METRICS,
                            value='temperature'
                        )
                    ]),
                    
                    # 预测天数
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('预测天数:'),
                        dcc.Slider(
                            id='forecast-days-slider',
                            min=1,
                            max=7,
                            step=1,
                            value=3,
                            marks={i: f'{i}天' for i in range(1, 8)}
                        )
                    ]),
                    
                    # 预测按钮
                    html.Div(style={'flex': '0 0 auto', 'display': 'flex', 'alignItems': 'flex-end'}, children=[
                        html.Button('开始预测', id='forecast-button', n_clicks=0, style={
                            'backgroundColor': '#f59e0b',
                            'color': 'white',
                            'border': 'none',
                            'padding': '0.5rem 1rem',
                            'borderRadius': '4px',
                            'cursor': 'pointer'
                        })
                    ])
                ])
            ]),
            
            # 预测结果
            html.Div(id='forecast-results', children=[
                html.Div(style={'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '1rem'}, children=[
                    html.H3(children='预测模型摘要', style={'marginTop': 0}),
                    html.Pre(id='model-summary', children='请先开始预测', style={'backgroundColor': '#f0f0f0', 'padding': '1rem', 'borderRadius': '4px', 'overflowX': 'auto'})
                ]),
                
                # 预测图表
                html.Div(style={'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '1rem'}, children=[
                    html.H3(children='预测结果图', style={'marginTop': 0}),
                    dcc.Graph(id='forecast-chart', figure=go.Figure(), style={'height': '400px'})
                ]),

                
                # 预测数据表格
                html.Div(style={'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                    html.H3(children='预测数据详情', style={'marginTop': 0}),
                    html.Table(id='forecast-table', children=[html.Tbody([html.Tr([html.Td('请先开始预测')])])])
                ])
            ])
        ]),
        
        # 智能预警标签页
        html.Div(id='alert-tab', style={'display': 'none'}, children=[
            # 预警设置
            html.Div(style={'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '1rem'}, children=[
                html.H3(children='预警设置', style={'marginTop': 0}),
                html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '1rem', 'alignItems': 'flex-start'}, children=[
                    # 城市选择
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('城市:'),
                        dcc.Dropdown(
                            id='alert-city-select',
                            options=[{'label': city.capitalize(), 'value': city} for city in CITIES],
                            value='beijing',
                            multi=True
                        )
                    ]),
                    
                    # 预警指标
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('预警指标:'),
                        dcc.Dropdown(
                            id='alert-metric-select',
                            options=METRICS,
                            value='temperature'
                        )
                    ]),
                    
                    # 预警阈值
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('预警阈值:'),
                        dcc.Input(id='alert-threshold', type='number', value=35, style={'width': '100%'})
                    ]),
                    
                    # 预警条件
                    html.Div(style={'flex': '1 1 200px'}, children=[
                        html.Label('预警条件:'),
                        dcc.Dropdown(
                            id='alert-operator',
                            options=[
                                {'label': '大于 (>)', 'value': '>'},
                                {'label': '小于 (<)', 'value': '<'},
                                {'label': '等于 (=)', 'value': '='}
                            ],
                            value='>'
                        )
                    ]),
                    
                    # 检查按钮
                    html.Div(style={'flex': '0 0 auto', 'display': 'flex', 'alignItems': 'flex-end'}, children=[
                        html.Button('检查预警', id='alert-check-button', n_clicks=0, style={
                            'backgroundColor': '#ef4444',
                            'color': 'white',
                            'border': 'none',
                            'padding': '0.5rem 1rem',
                            'borderRadius': '4px',
                            'cursor': 'pointer'
                        })
                    ])
                ])
            ]),
            
            # 预警结果
            html.Div(id='alert-results', children=[
                html.Div(style={'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '1rem'}, children=[
                    html.H3(children='预警状态', style={'marginTop': 0}),
                    html.Div(id='alert-status', children=html.P('请先设置预警参数并检查'))
                ]),
                
                # 预警历史
                html.Div(style={'backgroundColor': 'white', 'padding': '1rem', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
                    html.H3(children='预警历史', style={'marginTop': 0}),
                    html.Div(id='alert-history', children=html.P('暂无预警记录'))
                ])
            ])
        ])
    ]),
    
    # 页脚
    html.Div(style={'backgroundColor': '#1e3a8a', 'color': 'white', 'padding': '1rem', 'textAlign': 'center', 'marginTop': '2rem'}, children=[
        html.P(children='气象数据分析与可视化系统 © 2025', style={'margin': 0}),
        html.P(children='多源数据采集 · 合规校验 · 智能分析 · 可视化展示', style={'margin': '0.5rem 0 0 0'})
    ]),
    
    # 下载组件
    dcc.Download(id='download-chart')
])

# ------------------------------
# 回调函数
# ------------------------------

# 切换标签页
@app.callback(
    [Output('analysis-tab', 'style'),
     Output('extreme-events-tab', 'style'),
     Output('forecast-tab', 'style'),
     Output('alert-tab', 'style')],
    [Input('tabs', 'value')]
)
def switch_tab(tab_value):
    """切换标签页"""
    styles = {
        'analysis': {'display': 'block'},
        'extreme_events': {'display': 'block'},
        'forecast': {'display': 'block'},
        'alert': {'display': 'block'}
    }
    
    # 默认隐藏所有标签页
    result = [{'display': 'none'}] * 4
    
    if tab_value in styles:
        result[['analysis', 'extreme_events', 'forecast', 'alert'].index(tab_value)] = styles[tab_value]
    
    return result

# 获取数据
def get_data(cities, start_date, end_date):
    """获取数据"""
    all_data = pd.DataFrame()
    
    for city in cities:
        city_data = analyzer.get_historical_data(city, start_date, end_date)
        if not city_data.empty:
            city_data['city_name'] = city
            all_data = pd.concat([all_data, city_data])
    
    return all_data

# 更新主要图表
@app.callback(
    Output('main-chart', 'figure'),
    [Input('query-button', 'n_clicks')],
    [State('city-select', 'value'),
     State('metric-select', 'value'),
     State('time-period-select', 'value'),
     State('chart-type-select', 'value'),
     State('start-date', 'date'),
     State('end-date', 'date')]
)
def update_main_chart(n_clicks, cities, metric, time_period, chart_type, start_date, end_date):
    """更新主要图表"""
    if not cities:
        return go.Figure()
    
    # 确保cities是列表
    if not isinstance(cities, list):
        cities = [cities]
    
    # 获取数据
    df = get_data(cities, start_date, end_date)
    if df.empty:
        return go.Figure()
    
    # 准备图表标题
    title = f"{', '.join([city.capitalize() for city in cities])} - {METRIC_LABELS[metric]} ({TIME_PERIODS[[tp['value'] for tp in TIME_PERIODS].index(time_period)]['label']}趋势)"
    
    # 根据图表类型生成图表
    if chart_type == 'line':
        if len(cities) == 1:
            fig = charts.time_series_line_chart(df, metric=metric, title=title)
        else:
            # 多城市折线图
            fig = go.Figure()
            for city in cities:
                city_df = df[df['city_name'] == city]
                fig.add_trace(go.Scatter(
                    x=city_df.index,
                    y=city_df[metric],
                    mode='lines',
                    name=city.capitalize()
                ))
            fig.update_layout(
                title=title,
                xaxis_title='时间',
                yaxis_title=METRIC_LABELS[metric],
                template='plotly_white',
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
    elif chart_type == 'bar':
        if len(cities) == 1:
            # 单城市柱状图
            time_df = analyzer.time_dimension_analysis(cities[0], metric=metric, time_period=time_period)
            if not time_df.empty:
                fig = px.bar(time_df, 
                           y='平均值',
                           title=title,
                           labels={'平均值': METRIC_LABELS[metric]})
                fig.update_layout(
                    xaxis_title='时间',
                    yaxis_title=METRIC_LABELS[metric],
                    template='plotly_white'
                )
            else:
                fig = go.Figure()
        else:
            # 多城市分组柱状图
            fig = charts.grouped_bar_chart(df, metric=metric, time_period=time_period, title=title)
    elif chart_type == 'heatmap':
        # 时间-城市热力图
        fig = charts.time_city_heatmap(df, metric=metric, title=title)
    elif chart_type == 'radar':
        # 雷达图
        if len(cities) == 1:
            fig = charts.radar_chart(df, cities[0], metrics=[metric, 'pressure', 'humidity', 'wind_speed'], title=title)
        else:
            # 多城市雷达图，只显示温度
            fig = charts.multi_city_radar_chart(df, cities, metrics=[metric], title=title)
    elif chart_type == 'scatter':
        # 散点图
        if len(cities) == 1:
            fig = charts.scatter_plot(df, x_metric='temperature', y_metric=metric, title=title)
        else:
            fig = charts.scatter_with_regions(df, x_metric='temperature', y_metric=metric, title=title)
    elif chart_type == 'box':
        # 箱线图
        fig = charts.box_plot(df, metric=metric, title=title)
    elif chart_type == 'histogram':
        # 直方图
        fig = charts.histogram(df, metric=metric, title=title)
    else:
        fig = go.Figure()
    
    return fig

# 更新相关性热力图
@app.callback(
    Output('correlation-heatmap', 'figure'),
    [Input('query-button', 'n_clicks')],
    [State('city-select', 'value'),
     State('start-date', 'date'),
     State('end-date', 'date')]
)
def update_correlation_heatmap(n_clicks, cities, start_date, end_date):
    """更新相关性热力图"""
    if not cities:
        return go.Figure()
    
    # 确保cities是列表
    if not isinstance(cities, list):
        cities = [cities]
    
    # 使用第一个城市的数据
    df = analyzer.get_historical_data(cities[0], start_date, end_date)
    if df.empty:
        return go.Figure()
    
    # 计算相关性矩阵
    correlation_matrix = df[['temperature', 'pressure', 'humidity', 'precipitation', 'wind_speed', 'wind_direction']].corr()
    
    # 生成热力图
    fig = charts.correlation_heatmap(correlation_matrix, title=f"{cities[0].capitalize()} 气象指标相关性热力图")
    
    return fig

# 更新箱线图
@app.callback(
    Output('box-plot', 'figure'),
    [Input('query-button', 'n_clicks')],
    [State('city-select', 'value'),
     State('metric-select', 'value'),
     State('start-date', 'date'),
     State('end-date', 'date')]
)
def update_box_plot(n_clicks, cities, metric, start_date, end_date):
    """更新箱线图"""
    if not cities:
        return go.Figure()
    
    # 确保cities是列表
    if not isinstance(cities, list):
        cities = [cities]
    
    # 获取数据
    df = get_data(cities, start_date, end_date)
    if df.empty:
        return go.Figure()
    
    # 生成箱线图
    title = f"{', '.join([city.capitalize() for city in cities])} - {METRIC_LABELS[metric]} 分布箱线图"
    fig = charts.box_plot(df, metric=metric, title=title)
    
    return fig

# 更新直方图
@app.callback(
    Output('histogram', 'figure'),
    [Input('query-button', 'n_clicks')],
    [State('city-select', 'value'),
     State('metric-select', 'value'),
     State('start-date', 'date'),
     State('end-date', 'date')]
)
def update_histogram(n_clicks, cities, metric, start_date, end_date):
    """更新直方图"""
    if not cities:
        return go.Figure()
    
    # 确保cities是列表
    if not isinstance(cities, list):
        cities = [cities]
    
    # 获取数据
    df = get_data(cities, start_date, end_date)
    if df.empty:
        return go.Figure()
    
    # 生成直方图
    title = f"{', '.join([city.capitalize() for city in cities])} - {METRIC_LABELS[metric]} 分布直方图"
    fig = charts.histogram(df, metric=metric, title=title)
    
    return fig

# 更新极端事件图表
@app.callback(
    [Output('extreme-events-chart', 'figure'),
     Output('extreme-events-timeline', 'figure'),
     Output('extreme-events-table', 'children')],
    [Input('extreme-query-button', 'n_clicks')],
    [State('extreme-city-select', 'value'),
     State('extreme-start-date', 'date'),
     State('extreme-end-date', 'date')]
)
def update_extreme_events(n_clicks, cities, start_date, end_date):
    """更新极端事件图表"""
    if not cities:
        return go.Figure(), go.Figure(), html.P('请先选择城市')
    
    # 确保cities是列表
    if not isinstance(cities, list):
        cities = [cities]
    
    # 识别极端事件
    all_extreme_events = []
    for city in cities:
        extreme_events = analyzer.identify_extreme_events(city, start_date, end_date)
        all_extreme_events.extend(extreme_events)
    
    if not all_extreme_events:
        return go.Figure(), go.Figure(), html.P('未检测到极端事件')
    
    # 生成极端事件分布图
    event_chart = charts.extreme_events_chart(all_extreme_events, title='极端天气事件分布')
    
    # 生成极端事件时间线
    timeline_chart = charts.extreme_events_timeline(all_extreme_events, title='极端天气事件时间线')
    
    # 生成极端事件表格
    table_data = []
    for event in all_extreme_events[:20]:  # 只显示前20条
        table_data.append([
            event['city_name'].capitalize(),
            event['event_type'],
            event['timestamp'].strftime('%Y-%m-%d %H:%M'),
            event['metric'],
            f"{event['value']} {event['operator']} {event['threshold']}"
        ])
    
    table_header = html.Thead(html.Tr([
        html.Th('城市'),
        html.Th('事件类型'),
        html.Th('时间'),
        html.Th('指标'),
        html.Th('数值与阈值')
    ]))
    table_body = html.Tbody([html.Tr([html.Td(cell) for cell in row]) for row in table_data])
    table = html.Table([table_header, table_body], style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'})
    
    return event_chart, timeline_chart, table

# 更新预测结果
@app.callback(
    [Output('model-summary', 'children'),
     Output('forecast-chart', 'figure'),
     Output('forecast-table', 'children')],
    [Input('forecast-button', 'n_clicks')],
    [State('forecast-city-select', 'value'),
     State('forecast-metric-select', 'value'),
     State('forecast-days-slider', 'value')]
)
def update_forecast(n_clicks, city, metric, forecast_days):
    """更新预测结果"""
    # 获取历史数据
    historical_data = analyzer.get_historical_data(city)
    if historical_data.empty:
        return '未找到历史数据', go.Figure(), html.Tbody([html.Tr([html.Td('未找到历史数据')])])
    
    # 运行预测
    forecast_result = analyzer.arima_forecast(city, metric=metric, forecast_days=forecast_days)
    
    if not forecast_result['success']:
        return forecast_result['message'], go.Figure(), html.Tbody([html.Tr([html.Td(forecast_result['message'])])])
    
    # 生成预测图表
    fig = charts.forecast_chart(historical_data, forecast_result, metric=metric, title=f"{city.capitalize()} - {METRIC_LABELS[metric]} 未来{forecast_days}天预测")
    
    # 生成预测表格
    table_data = []
    for day in forecast_result['forecast_data']:
        table_data.append([
            day['date'],
            f"{day['predicted_value']:.1f}",
            f"[{day['lower_bound']:.1f}, {day['upper_bound']:.1f}]"
        ])
    
    table_header = html.Thead(html.Tr([
        html.Th('日期'),
        html.Th(f'预测{METRIC_LABELS[metric]}'),
        html.Th('95%置信区间')
    ]))
    table_body = html.Tbody([html.Tr([html.Td(cell) for cell in row]) for row in table_data])
    table = html.Table([table_header, table_body], style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'})
    
    return forecast_result['model_summary'], fig, table

# 更新预警结果
@app.callback(
    [Output('alert-status', 'children'),
     Output('alert-history', 'children')],
    [Input('alert-check-button', 'n_clicks')],
    [State('alert-city-select', 'value'),
     State('alert-metric-select', 'value'),
     State('alert-threshold', 'value'),
     State('alert-operator', 'value')]
)
def update_alert(n_clicks, cities, metric, threshold, operator):
    """更新预警结果"""
    if not cities:
        return html.P('请先选择城市'), html.P('暂无预警记录')
    
    # 确保cities是列表
    if not isinstance(cities, list):
        cities = [cities]
    
    # 构建预警阈值字典
    thresholds = {
        metric: {
            'operator': operator,
            'threshold': threshold
        }
    }
    
    # 检查预警
    all_alerts = []
    for city in cities:
        alerts = analyzer.check_weather_alerts(city, thresholds)
        all_alerts.extend(alerts)
    
    # 生成预警状态
    if all_alerts:
        alert_status = html.Div(style={'backgroundColor': '#fee2e2', 'color': '#dc2626', 'padding': '1rem', 'borderRadius': '4px'}, children=[
            html.H4(children='⚠️ 预警触发', style={'marginTop': 0}),
            html.Ul([
                html.Li(f"{alert['city_name'].capitalize()} - {METRIC_LABELS[alert['metric']]}: {alert['value']} {alert['operator']} {alert['threshold']}（{alert['time'].strftime('%Y-%m-%d %H:%M')}）")
                for alert in all_alerts
            ])
        ])
    else:
        alert_status = html.Div(style={'backgroundColor': '#d1fae5', 'color': '#065f46', 'padding': '1rem', 'borderRadius': '4px'}, children=[
            html.H4(children='✅ 无预警', style={'marginTop': 0}),
            html.P('当前所有指标均在正常范围内')
        ])
    
    # 获取历史预警数据（从最近的极端事件中获取）
    historical_alerts = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for city in cities:
        extreme_events = analyzer.identify_extreme_events(city, start_date, end_date)
        # 转换为预警历史格式
        for event in extreme_events[:10]:  # 只显示最近10条
            historical_alerts.append({
                'city': event['city_name'],
                'metric': event['metric'],
                'value': event['value'],
                'threshold': event['threshold'],
                'time': event['timestamp'].strftime('%Y-%m-%d %H:%M')
            })
    
    # 生成预警历史表格
    if historical_alerts:
        alert_history = html.Table([
            html.Thead(html.Tr([
                html.Th('城市'),
                html.Th('指标'),
                html.Th('数值'),
                html.Th('阈值'),
                html.Th('时间')
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(alert['city'].capitalize()),
                    html.Td(METRIC_LABELS[alert['metric']]),
                    html.Td(f"{alert['value']:.2f}"),
                    html.Td(alert['threshold']),
                    html.Td(alert['time'])
                ]) for alert in historical_alerts
            ])
        ], style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'})
    else:
        alert_history = html.P('暂无预警记录')
    
    return alert_status, alert_history

# 导出图表
@app.callback(
    Output('download-chart', 'data'),
    [Input('export-button', 'n_clicks')],
    [State('main-chart', 'figure'),
     State('city-select', 'value'),
     State('metric-select', 'value'),
     State('start-date', 'date'),
     State('end-date', 'date')],
    prevent_initial_call=True
)
def export_chart(n_clicks, figure, cities, metric, start_date, end_date):
    """导出图表"""
    if n_clicks > 0:
        # 确保cities是列表
        if not isinstance(cities, list):
            cities = [cities]
        
        # 获取数据
        df = get_data(cities, start_date, end_date)
        if not df.empty:
            # 导出数据为CSV
            return dcc.send_data_frame(df.to_csv, f"weather_data_{'_'.join(cities)}_{metric}_{start_date}_{end_date}.csv", index=True)
    return None

# ------------------------------
# 启动应用
# ------------------------------

if __name__ == '__main__':
    # 从环境变量获取配置
    host = os.getenv('DASH_HOST', '0.0.0.0')
    port = int(os.getenv('DASH_PORT', 8050))
    debug = os.getenv('DASH_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)
