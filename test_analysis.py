import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from analysis.data_analyzer import WeatherDataAnalyzer

def test_analysis_functions():
    """测试数据分析功能"""
    print("=== 开始测试数据分析功能 ===")
    
    analyzer = WeatherDataAnalyzer()
    
    try:
        # 测试1: 获取历史数据
        print("\n1. 测试获取历史数据...")
        df = analyzer.get_historical_data('beijing')
        print(f"   ✓ 获取到 {len(df)} 条数据")
        
        # 测试2: 时间维度分析
        print("\n2. 测试时间维度分析...")
        daily_analysis = analyzer.time_dimension_analysis('beijing', metric='temperature', time_period='daily')
        print(f"   ✓ 日维度分析结果: {len(daily_analysis)} 条")
        
        monthly_analysis = analyzer.time_dimension_analysis('beijing', metric='temperature', time_period='monthly')
        print(f"   ✓ 月维度分析结果: {len(monthly_analysis)} 条")
        
        seasonal_analysis = analyzer.time_dimension_analysis('beijing', metric='temperature', time_period='seasonal')
        print(f"   ✓ 季节维度分析结果: {len(seasonal_analysis)} 条")
        
        # 测试3: 区域维度分析
        print("\n3. 测试区域维度分析...")
        regional_analysis = analyzer.regional_dimension_analysis(metric='temperature', time_period='daily')
        print(f"   ✓ 区域分析结果: {len(regional_analysis)} 条记录")
        
        # 测试4: 关联维度分析
        print("\n4. 测试关联维度分析...")
        correlation = analyzer.correlation_analysis('beijing')
        print(f"   ✓ 相关性矩阵生成成功，形状: {correlation.shape}")
        
        # 测试5: 极端事件识别
        print("\n5. 测试极端事件识别...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        extreme_events = analyzer.identify_extreme_events('beijing', start_date, end_date)
        print(f"   ✓ 识别到 {len(extreme_events)} 个极端事件")
        
        # 测试6: ARIMA预测
        print("\n6. 测试ARIMA预测...")
        forecast_result = analyzer.arima_forecast('beijing', metric='temperature', forecast_days=3)
        if forecast_result['success']:
            print(f"   ✓ 预测成功，预测了 {len(forecast_result['forecast_data'])} 天")
            for day in forecast_result['forecast_data']:
                print(f"      {day['date']}: {day['predicted_value']:.1f}°C (置信区间: [{day['lower_bound']:.1f}, {day['upper_bound']:.1f}])")
        else:
            print(f"   ✓ 预测结果: {forecast_result['message']}")
        
        # 测试7: 预警功能
        print("\n7. 测试预警功能...")
        thresholds = {
            'temperature': {
                'operator': '>',
                'threshold': 35
            }
        }
        alerts = analyzer.check_weather_alerts('beijing', thresholds)
        print(f"   ✓ 预警检查完成，触发了 {len(alerts)} 个预警")
        
        print("\n=== 所有数据分析功能测试通过！ ===")
        
    except Exception as e:
        print(f"\n=== 测试失败: {e} ===")
        return False
    finally:
        analyzer.close()
    
    return True

if __name__ == "__main__":
    test_analysis_functions()