import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import os
from sqlalchemy.orm import sessionmaker
from processing.database_manager import DatabaseManager, HistoricalWeather, City, DataSource
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherDataAnalyzer:
    def __init__(self):
        # 初始化数据库连接管理器
        self.db_manager = DatabaseManager()
        
    def _get_session(self):
        """获取数据库会话，确保每次都是新的会话"""
        return self.db_manager.get_session()
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close()
    
    def get_historical_data(self, city_name=None, start_date=None, end_date=None):
        """获取历史气象数据"""
        session = None
        try:
            session = self._get_session()
            query = session.query(HistoricalWeather, City, DataSource).join(
                City, HistoricalWeather.city_id == City.city_id
            ).join(
                DataSource, HistoricalWeather.source_id == DataSource.source_id
            )
            
            if city_name:
                query = query.filter(City.city_name == city_name)
            
            if start_date:
                query = query.filter(HistoricalWeather.timestamp >= start_date)
            
            if end_date:
                query = query.filter(HistoricalWeather.timestamp <= end_date)
            
            results = query.all()
            
            # 转换为DataFrame
            data = []
            for weather, city, source in results:
                data.append({
                    'id': weather.id,
                    'city_id': city.city_id,
                    'city_name': city.city_name,
                    'source_id': source.source_id,
                    'source_name': source.source_name,
                    'timestamp': weather.timestamp,
                    'temperature': float(weather.temperature),
                    'pressure': float(weather.pressure),
                    'humidity': float(weather.humidity),
                    'precipitation': float(weather.precipitation),
                    'wind_speed': float(weather.wind_speed),
                    'wind_direction': float(weather.wind_direction),
                    'status': weather.status
                })
            
            df = pd.DataFrame(data)
            if not df.empty:
                df.set_index('timestamp', inplace=True)
            
            session.commit()
            return df
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"获取历史数据失败: {e}")
            return pd.DataFrame()
        finally:
            if session:
                session.close()
    
    # ------------------------------
    # 多维度数据分析功能
    # ------------------------------
    
    def time_dimension_analysis(self, city_name, metric='temperature', time_period='daily'):
        """时间维度分析
        
        Args:
            city_name: 城市名称
            metric: 指标名称 (temperature, pressure, humidity, precipitation, wind_speed, wind_direction)
            time_period: 时间周期 (daily, monthly, seasonal)
        
        Returns:
            分析结果DataFrame
        """
        try:
            # 获取数据
            df = self.get_historical_data(city_name)
            if df.empty:
                return pd.DataFrame()
            
            # 按时间周期分组
            if time_period == 'daily':
                # 按天分组，计算日平均值
                result = df.resample('D')[metric].agg(['mean', 'max', 'min', 'std'])
            elif time_period == 'monthly':
                # 按月分组，计算月平均值
                result = df.resample('ME')[metric].agg(['mean', 'max', 'min', 'std'])
            elif time_period == 'seasonal':
                # 按季节分组，计算季节平均值
                # 定义季节映射
                season_map = {
                    12: '冬季', 1: '冬季', 2: '冬季',
                    3: '春季', 4: '春季', 5: '春季',
                    6: '夏季', 7: '夏季', 8: '夏季',
                    9: '秋季', 10: '秋季', 11: '秋季'
                }
                
                # 添加季节列
                df['season'] = df.index.month.map(season_map)
                result = df.groupby('season')[metric].agg(['mean', 'max', 'min', 'std'])
                # 按季节顺序排序
                result = result.reindex(['春季', '夏季', '秋季', '冬季'])
            else:
                return pd.DataFrame()
            
            result.columns = ['平均值', '最大值', '最小值', '标准差']
            return result
        except Exception as e:
            logger.error(f"时间维度分析失败: {e}")
            return pd.DataFrame()
    
    def regional_dimension_analysis(self, metric='temperature', time_period='daily'):
        """区域维度分析
        
        Args:
            metric: 指标名称
            time_period: 时间周期
        
        Returns:
            分析结果DataFrame
        """
        try:
            # 获取所有城市数据
            df = self.get_historical_data()
            if df.empty:
                return pd.DataFrame()
            
            # 按城市和时间周期分组
            if time_period == 'daily':
                result = df.groupby(['city_name', pd.Grouper(freq='D')])[metric].mean().unstack(0)
            elif time_period == 'monthly':
                result = df.groupby(['city_name', pd.Grouper(freq='M')])[metric].mean().unstack(0)
            else:
                return pd.DataFrame()
            
            return result
        except Exception as e:
            logger.error(f"区域维度分析失败: {e}")
            return pd.DataFrame()
    
    def correlation_analysis(self, city_name):
        """关联维度分析
        
        Args:
            city_name: 城市名称
        
        Returns:
            相关性矩阵
        """
        try:
            # 获取数据
            df = self.get_historical_data(city_name)
            if df.empty:
                return pd.DataFrame()
            
            # 选择数值型指标
            numeric_cols = ['temperature', 'pressure', 'humidity', 'precipitation', 'wind_speed', 'wind_direction']
            df_numeric = df[numeric_cols]
            
            # 计算相关系数
            correlation_matrix = df_numeric.corr()
            
            return correlation_matrix
        except Exception as e:
            logger.error(f"关联维度分析失败: {e}")
            return pd.DataFrame()
    
    # ------------------------------
    # 极端事件识别功能
    # ------------------------------
    
    def identify_extreme_events(self, city_name, start_date=None, end_date=None):
        """识别极端天气事件
        
        Args:
            city_name: 城市名称
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            极端事件列表
        """
        try:
            # 获取数据
            df = self.get_historical_data(city_name, start_date, end_date)
            if df.empty:
                return []
            
            extreme_events = []
            
            # 定义极端事件识别规则
            rules = {
                '高温': {
                    'metric': 'temperature',
                    'threshold': 35,
                    'operator': '>'
                },
                '低温': {
                    'metric': 'temperature',
                    'threshold': -10,
                    'operator': '<'
                },
                '暴雨': {
                    'metric': 'precipitation',
                    'threshold': 50,
                    'operator': '>'
                },
                '大风': {
                    'metric': 'wind_speed',
                    'threshold': 20,
                    'operator': '>'
                },
                '高湿': {
                    'metric': 'humidity',
                    'threshold': 95,
                    'operator': '>'
                },
                '干燥': {
                    'metric': 'humidity',
                    'threshold': 20,
                    'operator': '<'
                }
            }
            
            # 识别极端事件
            for event_type, rule in rules.items():
                metric = rule['metric']
                threshold = rule['threshold']
                operator = rule['operator']
                
                if operator == '>':
                    extreme_df = df[df[metric] > threshold]
                elif operator == '<':
                    extreme_df = df[df[metric] < threshold]
                else:
                    continue
                
                for timestamp, row in extreme_df.iterrows():
                    extreme_events.append({
                        'event_type': event_type,
                        'city_name': city_name,
                        'timestamp': timestamp,
                        'metric': metric,
                        'value': float(row[metric]),
                        'threshold': threshold,
                        'operator': operator,
                        'temperature': float(row['temperature']),
                        'pressure': float(row['pressure']),
                        'humidity': float(row['humidity']),
                        'precipitation': float(row['precipitation']),
                        'wind_speed': float(row['wind_speed']),
                        'wind_direction': float(row['wind_direction'])
                    })
            
            # 按时间排序
            extreme_events.sort(key=lambda x: x['timestamp'])
            
            return extreme_events
        except Exception as e:
            logger.error(f"识别极端事件失败: {e}")
            return []
    
    # ------------------------------
    # 短期气象预测功能
    # ------------------------------
    
    def arima_forecast(self, city_name, metric='temperature', forecast_days=3):
        """基于ARIMA模型的短期气象预测
        
        Args:
            city_name: 城市名称
            metric: 指标名称
            forecast_days: 预测天数
        
        Returns:
            预测结果字典
        """
        try:
            # 获取数据
            df = self.get_historical_data(city_name)
            if df.empty:
                return {
                    'success': False,
                    'message': '没有找到足够的数据进行预测'
                }
            
            # 选择指标数据并按日重采样
            data = df[metric].resample('D').mean().dropna()
            
            if len(data) < 10:  # 降低数据量要求，便于测试
                return {
                    'success': False,
                    'message': f'数据量不足，当前有 {len(data)} 天数据，需要至少10天'
                }
            
            # 为时间序列设置频率
            data = data.asfreq('D')
            
            # 尝试不同的ARIMA参数组合，提高模型鲁棒性
            try:
                # 先尝试简单的ARIMA模型
                model = ARIMA(data, order=(2, 1, 1))  # 更保守的参数设置
                model_fit = model.fit()
            except Exception as e1:
                try:
                    # 尝试更简单的模型
                    model = ARIMA(data, order=(1, 1, 0))
                    model_fit = model.fit()
                except Exception as e2:
                    return {
                        'success': False,
                        'message': f'模型训练失败: {str(e2)}'
                    }
            
            # 进行预测
            forecast_result = model_fit.get_forecast(steps=forecast_days)
            forecast = forecast_result.predicted_mean
            confidence_intervals = forecast_result.conf_int()
            
            # 准备结果
            last_date = data.index[-1]
            forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days, freq='D')
            
            forecast_dict = {
                'success': True,
                'city_name': city_name,
                'metric': metric,
                'forecast_days': forecast_days,
                'forecast_data': [],
                'model_summary': str(model_fit.summary())
            }
            
            # 确保预测结果和日期长度匹配
            min_length = min(len(forecast), len(forecast_dates), len(confidence_intervals))
            
            for i in range(min_length):
                forecast_dict['forecast_data'].append({
                    'date': forecast_dates[i].strftime('%Y-%m-%d'),
                    'predicted_value': float(forecast.iloc[i]) if hasattr(forecast, 'iloc') else float(forecast[i]),
                    'lower_bound': float(confidence_intervals.iloc[i, 0]),
                    'upper_bound': float(confidence_intervals.iloc[i, 1])
                })
            
            return forecast_dict
        except Exception as e:
            logger.error(f"ARIMA预测失败: {str(e)}")
            return {
                'success': False,
                'message': f'预测失败: {str(e)}'
            }
    
    # ------------------------------
    # 数据导出功能
    # ------------------------------
    
    def export_analysis_results(self, data, file_path, file_format='csv'):
        """导出分析结果
        
        Args:
            data: 要导出的数据 (DataFrame或列表)
            file_path: 导出文件路径
            file_format: 导出格式 (csv, excel, json)
        
        Returns:
            bool: 导出是否成功
        """
        try:
            if isinstance(data, pd.DataFrame):
                if file_format == 'csv':
                    data.to_csv(file_path)
                elif file_format == 'excel':
                    data.to_excel(file_path, index=True)
                elif file_format == 'json':
                    data.to_json(file_path, orient='records')
                else:
                    logger.error(f"不支持的导出格式: {file_format}")
                    return False
            elif isinstance(data, list):
                if file_format == 'json':
                    import json
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, default=str)
                else:
                    logger.error(f"列表数据仅支持JSON格式导出")
                    return False
            else:
                logger.error(f"不支持的数据类型: {type(data)}")
                return False
            
            logger.info(f"分析结果成功导出到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"导出分析结果失败: {e}")
            return False
    
    # ------------------------------
    # 极端天气预警功能
    # ------------------------------
    
    def check_weather_alerts(self, city_name, thresholds):
        """检查天气预警
        
        Args:
            city_name: 城市名称
            thresholds: 预警阈值字典，格式为:
                       {'metric': {'operator': '>', 'threshold': value}}
                       例如: {'temperature': {'operator': '>', 'threshold': 35}}
        
        Returns:
            list: 触发的预警列表
        """
        try:
            # 获取最新数据（最近24小时）
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            df = self.get_historical_data(city_name, start_date, end_date)
            if df.empty:
                return []
            
            alerts = []
            for metric, rule in thresholds.items():
                if metric in df.columns:
                    operator = rule['operator']
                    threshold = rule['threshold']
                    
                    # 检查最新数据
                    latest_value = float(df[metric].iloc[-1])
                    latest_time = df.index[-1]
                    
                    alert_triggered = False
                    if operator == '>' and latest_value > threshold:
                        alert_triggered = True
                    elif operator == '<' and latest_value < threshold:
                        alert_triggered = True
                    elif operator == '>=' and latest_value >= threshold:
                        alert_triggered = True
                    elif operator == '<=' and latest_value <= threshold:
                        alert_triggered = True
                    elif operator == '==' and latest_value == threshold:
                        alert_triggered = True
                    
                    if alert_triggered:
                        alerts.append({
                            'city_name': city_name,
                            'metric': metric,
                            'value': latest_value,
                            'threshold': threshold,
                            'operator': operator,
                            'time': latest_time,
                            'alert_level': 'high' if abs(latest_value - threshold) > threshold * 0.1 else 'medium'
                        })
            
            return alerts
        except Exception as e:
            logger.error(f"检查天气预警失败: {e}")
            return []

# 示例用法
if __name__ == "__main__":
    analyzer = WeatherDataAnalyzer()
    
    try:
        # 示例1: 时间维度分析
        logger.info("=== 时间维度分析示例 ===")
        daily_temp = analyzer.time_dimension_analysis('beijing', metric='temperature', time_period='daily')
        if not daily_temp.empty:
            logger.info(f"北京日平均温度分析结果 (前10条):")
            logger.info(daily_temp.head(10))
        
        # 示例2: 区域维度分析
        logger.info("\n=== 区域维度分析示例 ===")
        regional_temp = analyzer.regional_dimension_analysis(metric='temperature', time_period='daily')
        if not regional_temp.empty:
            logger.info(f"各城市日平均温度对比 (前10条):")
            logger.info(regional_temp.head(10))
        
        # 示例3: 关联维度分析
        logger.info("\n=== 关联维度分析示例 ===")
        correlation = analyzer.correlation_analysis('beijing')
        if not correlation.empty:
            logger.info(f"北京各指标相关性矩阵:")
            logger.info(correlation)
        
        # 示例4: 极端事件识别
        logger.info("\n=== 极端事件识别示例 ===")
        extreme_events = analyzer.identify_extreme_events('beijing')
        logger.info(f"识别到 {len(extreme_events)} 个极端事件")
        if extreme_events:
            logger.info(f"最近的5个极端事件:")
            for event in extreme_events[-5:]:
                logger.info(f"{event['event_type']}: {event['timestamp']} - {event['metric']}: {event['value']} {event['operator']} {event['threshold']}")
        
        # 示例5: ARIMA预测
        logger.info("\n=== ARIMA预测示例 ===")
        forecast_result = analyzer.arima_forecast('beijing', metric='temperature', forecast_days=3)
        if forecast_result['success']:
            logger.info(f"北京未来3天温度预测:")
            for day in forecast_result['forecast_data']:
                logger.info(f"{day['date']}: {day['predicted_value']:.1f}°C (置信区间: [{day['lower_bound']:.1f}, {day['upper_bound']:.1f}])")
        else:
            logger.error(f"预测失败: {forecast_result['message']}")
    
    finally:
        analyzer.close()
