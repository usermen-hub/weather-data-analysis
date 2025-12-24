import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
from meteostat import Point, Daily, Hourly
import pyowm
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class WeatherDataCollector:
    def __init__(self):
        self.api_keys = {
            'owm': os.getenv('OPENWEATHER_API_KEY'),
            'openweather': os.getenv('OPENWEATHER_API_KEY')
        }
        
        # 初始化OpenWeatherMap客户端
        if self.api_keys['owm']:
            self.owm = pyowm.OWM(self.api_keys['owm'])
            self.mgr = self.owm.weather_manager()
        
        # 城市坐标映射
        self.city_coords = {
            'beijing': (39.9042, 116.4074),
            'shanghai': (31.2304, 121.4737),
            'guangzhou': (23.1291, 113.2644),
            'shenzhen': (22.5431, 114.0579),
            'chengdu': (30.5728, 104.0668)
        }
    
    def get_realtime_weather(self, city='beijing'):
        """获取实时气象数据"""
        try:
            if city not in self.city_coords:
                logger.error(f"城市 {city} 不在支持列表中")
                return None
            
            # 检查是否有API密钥
            if not hasattr(self, 'mgr'):
                logger.warning(f"未配置OpenWeatherMap API密钥，无法获取 {city} 实时气象数据")
                return None
            
            lat, lon = self.city_coords[city]
            
            # 使用OpenWeatherMap获取实时数据
            weather = self.mgr.weather_at_coords(lat, lon).weather
            
            data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'city': city,
                'temperature': weather.temperature('celsius')['temp'],
                'pressure': weather.pressure['press'],
                'humidity': weather.humidity,
                'precipitation': weather.rain.get('1h', 0) if hasattr(weather, 'rain') else 0,
                'wind_speed': weather.wind()['speed'],
                'wind_direction': weather.wind()['deg'],
                'source': 'OpenWeatherMap'
            }
            
            logger.info(f"成功获取 {city} 实时气象数据")
            return data
            
        except Exception as e:
            logger.error(f"获取实时气象数据失败: {e}")
            return None
    
    def get_historical_weather(self, city='beijing', start_date=None, end_date=None):
        """获取历史气象数据"""
        try:
            if city not in self.city_coords:
                logger.error(f"城市 {city} 不在支持列表中")
                return None
            
            lat, lon = self.city_coords[city]
            point = Point(lat, lon)
            
            # 设置默认时间范围（最近30天）
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # 使用Meteostat获取历史数据
            data = Hourly(point, start_date, end_date)
            data = data.fetch()
            
            if data.empty:
                logger.warning(f"未获取到 {city} 在 {start_date} 至 {end_date} 期间的历史数据")
                return None
            
            # 选择并重命名需要的列
            data = data[['temp', 'pres', 'rhum', 'prcp', 'wspd', 'wdir']]
            data.columns = ['temperature', 'pressure', 'humidity', 'precipitation', 'wind_speed', 'wind_direction']
            
            # 添加城市和时间戳
            data['city'] = city
            data['timestamp'] = data.index.strftime('%Y-%m-%d %H:%M:%S')
            data['source'] = 'Meteostat'
            
            # 重置索引
            data = data.reset_index(drop=True)
            
            logger.info(f"成功获取 {city} 历史气象数据，共 {len(data)} 条记录")
            return data
            
        except Exception as e:
            logger.error(f"获取历史气象数据失败: {e}")
            return None
    
    def download_kaggle_dataset(self, dataset_name='brendon157/extreme-weather-events', save_path='./data'):
        """从Kaggle下载极端天气数据集"""
        try:
            # 确保保存路径存在
            os.makedirs(save_path, exist_ok=True)
            
            # 使用kaggle API下载数据集
            import kaggle
            kaggle.api.authenticate()
            kaggle.api.dataset_download_files(dataset_name, path=save_path, unzip=True)
            
            logger.info(f"成功下载Kaggle极端天气数据集到 {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"下载Kaggle数据集失败: {e}")
            return False
    
    def save_data(self, data, filename, data_type='realtime'):
        """保存数据到文件"""
        try:
            # 确保数据目录存在
            os.makedirs('./data', exist_ok=True)
            
            if data_type == 'realtime':
                # 实时数据保存为JSON
                df = pd.DataFrame([data])
                df.to_json(f'./data/{filename}.json', orient='records', indent=2)
            else:
                # 历史数据保存为CSV
                data.to_csv(f'./data/{filename}.csv', index=False)
            
            logger.info(f"数据已保存到 ./data/{filename}.{'json' if data_type=='realtime' else 'csv'}")
            return True
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            return False

if __name__ == "__main__":
    collector = WeatherDataCollector()
    
    # 获取实时数据
    realtime_data = collector.get_realtime_weather('beijing')
    if realtime_data:
        collector.save_data(realtime_data, f'realtime_weather_beijing_{datetime.now().strftime("%Y%m%d_%H%M%S")}', 'realtime')
    
    # 获取历史数据
    historical_data = collector.get_historical_weather('beijing')
    if historical_data is not None:
        collector.save_data(historical_data, f'historical_weather_beijing_{datetime.now().strftime("%Y%m%d")}', 'historical')
    
    # 下载Kaggle数据集
    collector.download_kaggle_dataset()