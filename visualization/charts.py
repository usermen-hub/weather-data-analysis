import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class WeatherCharts:
    def __init__(self):
        pass
    
    # ------------------------------
    # 时间趋势折线图
    # ------------------------------
    def time_series_line_chart(self, df, metric='temperature', title='时间趋势分析'):
        """生成时间序列折线图
        
        Args:
            df: 数据DataFrame，索引为时间
            metric: 指标名称
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            fig = px.line(df, 
                         y=metric, 
                         title=title,
                         labels={metric: metric.capitalize(), 'timestamp': '时间'})
            
            fig.update_layout(
                xaxis_title='时间',
                yaxis_title=metric.capitalize(),
                template='plotly_white',
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            print(f"生成时间序列折线图失败: {e}")
            return go.Figure()
    
    def multi_metric_line_chart(self, df, metrics=['temperature', 'humidity', 'pressure'], title='多指标时间趋势'):
        """生成多指标时间序列折线图
        
        Args:
            df: 数据DataFrame，索引为时间
            metrics: 指标列表
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            fig = go.Figure()
            
            for metric in metrics:
                if metric in df.columns:
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df[metric],
                        mode='lines',
                        name=metric.capitalize()
                    ))
            
            fig.update_layout(
                title=title,
                xaxis_title='时间',
                yaxis_title='数值',
                template='plotly_white',
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            return fig
        except Exception as e:
            print(f"生成多指标时间序列折线图失败: {e}")
            return go.Figure()
    
    # ------------------------------
    # 区域对比柱状图
    # ------------------------------
    def regional_comparison_bar_chart(self, df, metric='temperature', title='区域对比分析'):
        """生成区域对比柱状图
        
        Args:
            df: 数据DataFrame，包含city_name列和指定metric列
            metric: 指标名称
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            if isinstance(df, pd.DataFrame) and not df.empty:
                # 如果索引是时间，先聚合数据
                if isinstance(df.index, pd.DatetimeIndex):
                    df = df.reset_index()
                
                # 计算每个城市的平均值
                city_avg = df.groupby('city_name')[metric].mean().reset_index()
                
                fig = px.bar(city_avg, 
                           x='city_name', 
                           y=metric,
                           title=title,
                           labels={metric: metric.capitalize(), 'city_name': '城市'})
                
                fig.update_layout(
                    xaxis_title='城市',
                    yaxis_title=metric.capitalize(),
                    template='plotly_white',
                    hovermode='x unified'
                )
                
                return fig
            return go.Figure()
        except Exception as e:
            print(f"生成区域对比柱状图失败: {e}")
            return go.Figure()
    
    def grouped_bar_chart(self, df, metric='temperature', time_period='daily', title='分组柱状图'):
        """生成分组柱状图
        
        Args:
            df: 数据DataFrame，包含city_name列和指定metric列
            metric: 指标名称
            time_period: 时间周期
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            if isinstance(df, pd.DataFrame) and not df.empty:
                # 确保数据格式正确
                if isinstance(df.index, pd.DatetimeIndex):
                    df = df.reset_index()
                
                # 转换时间格式
                df['time'] = df['timestamp'].dt.strftime('%Y-%m-%d') if time_period == 'daily' else df['timestamp'].dt.strftime('%Y-%m')
                
                fig = px.bar(df, 
                           x='time', 
                           y=metric,
                           color='city_name',
                           barmode='group',
                           title=title,
                           labels={metric: metric.capitalize(), 'time': '时间', 'city_name': '城市'})
                
                fig.update_layout(
                    xaxis_title='时间',
                    yaxis_title=metric.capitalize(),
                    template='plotly_white',
                    hovermode='x unified',
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
                )
                
                return fig
            return go.Figure()
        except Exception as e:
            print(f"生成分组柱状图失败: {e}")
            return go.Figure()
    
    # ------------------------------
    # 相关性热力图
    # ------------------------------
    def correlation_heatmap(self, correlation_matrix, title='指标相关性热力图'):
        """生成相关性热力图
        
        Args:
            correlation_matrix: 相关性矩阵DataFrame
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            fig = px.imshow(correlation_matrix,
                          text_auto=True,
                          title=title,
                          color_continuous_scale='RdBu_r',
                          range_color=[-1, 1])
            
            fig.update_layout(
                template='plotly_white',
                xaxis_title='指标',
                yaxis_title='指标'
            )
            
            return fig
        except Exception as e:
            print(f"生成相关性热力图失败: {e}")
            return go.Figure()
    
    # ------------------------------
    # 雷达图
    # ------------------------------
    def radar_chart(self, df, city_name, metrics=['temperature', 'pressure', 'humidity', 'wind_speed'], title='城市气象指标雷达图'):
        """生成雷达图
        
        Args:
            df: 数据DataFrame，包含city_name列和指定metrics列
            city_name: 城市名称
            metrics: 指标列表
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            # 获取指定城市的数据
            city_df = df[df['city_name'] == city_name]
            if city_df.empty:
                return go.Figure()
            
            # 计算平均值
            avg_values = city_df[metrics].mean().values
            
            # 准备雷达图数据
            fig = go.Figure(data=go.Scatterpolar(
                r=avg_values,
                theta=[m.capitalize() for m in metrics],
                fill='toself',
                name=city_name
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(avg_values) * 1.2]
                    )),
                showlegend=True,
                title=title,
                template='plotly_white'
            )
            
            return fig
        except Exception as e:
            print(f"生成雷达图失败: {e}")
            return go.Figure()
    
    def multi_city_radar_chart(self, df, cities, metrics=['temperature', 'pressure', 'humidity', 'wind_speed'], title='多城市气象指标雷达图'):
        """生成多城市雷达图
        
        Args:
            df: 数据DataFrame，包含city_name列和指定metrics列
            cities: 城市列表
            metrics: 指标列表
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            fig = go.Figure()
            
            for city in cities:
                city_df = df[df['city_name'] == city]
                if not city_df.empty:
                    avg_values = city_df[metrics].mean().values
                    fig.add_trace(go.Scatterpolar(
                        r=avg_values,
                        theta=[m.capitalize() for m in metrics],
                        fill='toself',
                        name=city
                    ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]  # 假设所有指标都已归一化到[0, 100]
                    )),
                showlegend=True,
                title=title,
                template='plotly_white',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            return fig
        except Exception as e:
            print(f"生成多城市雷达图失败: {e}")
            return go.Figure()
    
    # ------------------------------
    # 散点图
    # ------------------------------
    def scatter_plot(self, df, x_metric='temperature', y_metric='humidity', title='指标关系散点图'):
        """生成散点图
        
        Args:
            df: 数据DataFrame，包含x_metric和y_metric列
            x_metric: x轴指标
            y_metric: y轴指标
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            fig = px.scatter(df, 
                           x=x_metric, 
                           y=y_metric,
                           title=title,
                           trendline='ols',
                           labels={x_metric: x_metric.capitalize(), y_metric: y_metric.capitalize()})
            
            fig.update_layout(
                xaxis_title=x_metric.capitalize(),
                yaxis_title=y_metric.capitalize(),
                template='plotly_white',
                hovermode='closest'
            )
            
            return fig
        except Exception as e:
            print(f"生成散点图失败: {e}")
            return go.Figure()
    
    def scatter_with_regions(self, df, x_metric='temperature', y_metric='humidity', title='区域指标关系散点图'):
        """生成带区域标记的散点图
        
        Args:
            df: 数据DataFrame，包含x_metric、y_metric和city_name列
            x_metric: x轴指标
            y_metric: y轴指标
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            fig = px.scatter(df, 
                           x=x_metric, 
                           y=y_metric,
                           color='city_name',
                           title=title,
                           trendline='ols',
                           labels={x_metric: x_metric.capitalize(), y_metric: y_metric.capitalize(), 'city_name': '城市'})
            
            fig.update_layout(
                xaxis_title=x_metric.capitalize(),
                yaxis_title=y_metric.capitalize(),
                template='plotly_white',
                hovermode='closest',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            return fig
        except Exception as e:
            print(f"生成带区域标记的散点图失败: {e}")
            return go.Figure()
    
    # ------------------------------
    # 热力图（时间-城市）
    # ------------------------------
    def time_city_heatmap(self, df, metric='temperature', title='时间-城市热力图'):
        """生成时间-城市热力图
        
        Args:
            df: 数据DataFrame，包含timestamp、city_name和指定metric列
            metric: 指标名称
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            if isinstance(df, pd.DataFrame) and not df.empty:
                # 确保数据格式正确
                if isinstance(df.index, pd.DatetimeIndex):
                    df = df.reset_index()
                
                # 创建透视表
                pivot_df = df.pivot(index='city_name', columns='timestamp', values=metric)
                
                fig = px.imshow(pivot_df,
                              title=title,
                              labels=dict(x='时间', y='城市', color=metric.capitalize()),
                              color_continuous_scale='RdBu_r')
                
                fig.update_layout(
                    template='plotly_white',
                    xaxis_tickangle=-45
                )
                
                return fig
            return go.Figure()
        except Exception as e:
            print(f"生成时间-城市热力图失败: {e}")
            return go.Figure()
    
    # ------------------------------
    # 预测结果图
    # ------------------------------
    def forecast_chart(self, historical_data, forecast_data, metric='temperature', title='短期气象预测'):
        """生成预测结果图
        
        Args:
            historical_data: 历史数据DataFrame，索引为时间
            forecast_data: 预测结果字典，包含forecast_data列表
            metric: 指标名称
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            fig = go.Figure()
            
            # 添加历史数据
            fig.add_trace(go.Scatter(
                x=historical_data.index,
                y=historical_data[metric],
                mode='lines',
                name='历史数据',
                line=dict(color='blue')
            ))
            
            # 提取预测数据
            forecast_dates = []
            predicted_values = []
            lower_bounds = []
            upper_bounds = []
            
            for day in forecast_data['forecast_data']:
                forecast_dates.append(pd.to_datetime(day['date']))
                predicted_values.append(day['predicted_value'])
                lower_bounds.append(day['lower_bound'])
                upper_bounds.append(day['upper_bound'])
            
            # 添加预测数据
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=predicted_values,
                mode='lines+markers',
                name='预测值',
                line=dict(color='red', dash='dash')
            ))
            
            # 添加置信区间
            fig.add_trace(go.Scatter(
                x=forecast_dates + forecast_dates[::-1],
                y=upper_bounds + lower_bounds[::-1],
                fill='toself',
                fillcolor='rgba(255, 0, 0, 0.2)',
                line=dict(color='rgba(255, 255, 255, 0)'),
                name='95%置信区间'
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title='时间',
                yaxis_title=metric.capitalize(),
                template='plotly_white',
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            return fig
        except Exception as e:
            print(f"生成预测结果图失败: {e}")
            return go.Figure()
    
    # ------------------------------
    # 极端事件图表
    # ------------------------------
    def extreme_events_chart(self, extreme_events, title='极端天气事件分布'):
        """生成极端事件图表
        
        Args:
            extreme_events: 极端事件列表
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            # 转换为DataFrame
            df = pd.DataFrame(extreme_events)
            if df.empty:
                return go.Figure()
            
            # 按事件类型分组
            event_counts = df['event_type'].value_counts().reset_index()
            event_counts.columns = ['event_type', 'count']
            
            fig = px.bar(event_counts,
                        x='event_type',
                        y='count',
                        title=title,
                        labels={'event_type': '事件类型', 'count': '发生次数'})
            
            fig.update_layout(
                xaxis_title='事件类型',
                yaxis_title='发生次数',
                template='plotly_white',
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            print(f"生成极端事件图表失败: {e}")
            return go.Figure()
    
    def extreme_events_timeline(self, extreme_events, title='极端天气事件时间线'):
        """生成极端事件时间线
        
        Args:
            extreme_events: 极端事件列表
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            # 转换为DataFrame
            df = pd.DataFrame(extreme_events)
            if df.empty:
                return go.Figure()
            
            # 按时间排序
            df.sort_values('timestamp', inplace=True)
            
            fig = px.scatter(df,
                           x='timestamp',
                           y='event_type',
                           size='value',
                           color='city_name',
                           title=title,
                           labels={'timestamp': '时间', 'event_type': '事件类型', 'value': '指标值', 'city_name': '城市'})
            
            fig.update_layout(
                xaxis_title='时间',
                yaxis_title='事件类型',
                template='plotly_white',
                hovermode='closest',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            return fig
        except Exception as e:
            print(f"生成极端事件时间线失败: {e}")
            return go.Figure()
    
    # ------------------------------
    # 统计图表
    # ------------------------------
    def box_plot(self, df, metric='temperature', title='指标分布箱线图'):
        """生成箱线图
        
        Args:
            df: 数据DataFrame，包含metric列
            metric: 指标名称
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            fig = px.box(df, 
                        y=metric,
                        title=title,
                        labels={metric: metric.capitalize()})
            
            fig.update_layout(
                yaxis_title=metric.capitalize(),
                template='plotly_white'
            )
            
            return fig
        except Exception as e:
            print(f"生成箱线图失败: {e}")
            return go.Figure()
    
    def histogram(self, df, metric='temperature', title='指标分布直方图'):
        """生成直方图
        
        Args:
            df: 数据DataFrame，包含metric列
            metric: 指标名称
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            fig = px.histogram(df, 
                             x=metric,
                             title=title,
                             labels={metric: metric.capitalize()},
                             nbins=30)
            
            fig.update_layout(
                xaxis_title=metric.capitalize(),
                yaxis_title='频率',
                template='plotly_white'
            )
            
            return fig
        except Exception as e:
            print(f"生成直方图失败: {e}")
            return go.Figure()
