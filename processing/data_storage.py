import os
import logging
from datetime import datetime
import pandas as pd
from sqlalchemy.exc import IntegrityError

from .database_manager import DatabaseManager, RealTimeWeather, HistoricalWeather, ExtremeEvent, DataCleaningLog
from .data_preprocessor import WeatherDataPreprocessor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherDataStorage:
    def __init__(self):
        # 初始化数据库管理器
        self.db_manager = DatabaseManager()
        
        # 初始化数据预处理模块
        self.preprocessor = WeatherDataPreprocessor()
    
    def store_realtime_weather(self, df):
        """存储实时气象数据"""
        try:
            session = self.db_manager.get_session()
            stored_count = 0
            updated_count = 0
            
            for _, row in df.iterrows():
                # 检查数据是否已存在
                existing_data = session.query(RealTimeWeather).filter(
                    RealTimeWeather.city_id == row['city_id'],
                    RealTimeWeather.timestamp == row['timestamp']
                ).first()
                
                if existing_data:
                    # 更新现有数据
                    existing_data.source_id = row['source_id']
                    existing_data.temperature = row['temperature']
                    existing_data.pressure = row['pressure']
                    existing_data.humidity = row['humidity']
                    existing_data.precipitation = row['precipitation']
                    existing_data.wind_speed = row['wind_speed']
                    existing_data.wind_direction = row['wind_direction']
                    existing_data.status = 1
                    updated_count += 1
                else:
                    # 插入新数据
                    realtime_data = RealTimeWeather(
                        city_id=row['city_id'],
                        source_id=row['source_id'],
                        timestamp=row['timestamp'],
                        temperature=row['temperature'],
                        pressure=row['pressure'],
                        humidity=row['humidity'],
                        precipitation=row['precipitation'],
                        wind_speed=row['wind_speed'],
                        wind_direction=row['wind_direction'],
                        status=1
                    )
                    session.add(realtime_data)
                    stored_count += 1
            
            # 提交事务
            session.commit()
            session.close()
            
            logger.info(f"实时气象数据存储完成，新增: {stored_count}条，更新: {updated_count}条")
            return True, stored_count, updated_count
        except IntegrityError as e:
            logger.error(f"实时气象数据存储失败，完整性错误: {e}")
            session.rollback()
            session.close()
            return False, 0, 0
        except Exception as e:
            logger.error(f"实时气象数据存储失败: {e}")
            session.rollback()
            session.close()
            return False, 0, 0
    
    def store_historical_weather(self, df):
        """存储历史气象数据"""
        try:
            session = self.db_manager.get_session()
            stored_count = 0
            
            for _, row in df.iterrows():
                # 检查数据是否已存在
                existing_data = session.query(HistoricalWeather).filter(
                    HistoricalWeather.city_id == row['city_id'],
                    HistoricalWeather.timestamp == row['timestamp']
                ).first()
                
                if not existing_data:
                    # 插入新数据
                    historical_data = HistoricalWeather(
                        city_id=row['city_id'],
                        source_id=row['source_id'],
                        timestamp=row['timestamp'],
                        temperature=row['temperature'],
                        pressure=row['pressure'],
                        humidity=row['humidity'],
                        precipitation=row['precipitation'],
                        wind_speed=row['wind_speed'],
                        wind_direction=row['wind_direction'],
                        status=1
                    )
                    session.add(historical_data)
                    stored_count += 1
            
            # 提交事务
            session.commit()
            session.close()
            
            logger.info(f"历史气象数据存储完成，新增: {stored_count}条")
            return True, stored_count
        except IntegrityError as e:
            logger.error(f"历史气象数据存储失败，完整性错误: {e}")
            session.rollback()
            session.close()
            return False, 0
        except Exception as e:
            logger.error(f"历史气象数据存储失败: {e}")
            session.rollback()
            session.close()
            return False, 0
    
    def store_extreme_events(self, df):
        """存储极端天气事件数据"""
        try:
            session = self.db_manager.get_session()
            stored_count = 0
            
            for _, row in df.iterrows():
                # 检查数据是否已存在
                existing_event = session.query(ExtremeEvent).filter(
                    ExtremeEvent.city_id == row['city_id'],
                    ExtremeEvent.event_type == row['event_type'],
                    ExtremeEvent.start_time == row['start_time'],
                    ExtremeEvent.end_time == row['end_time']
                ).first()
                
                if not existing_event:
                    # 插入新数据
                    extreme_event = ExtremeEvent(
                        city_id=row['city_id'],
                        source_id=row['source_id'],
                        event_type=row['event_type'],
                        event_level=row['event_level'],
                        start_time=row['start_time'],
                        end_time=row['end_time'],
                        max_temperature=row.get('max_temperature'),
                        min_temperature=row.get('min_temperature'),
                        max_pressure=row.get('max_pressure'),
                        min_pressure=row.get('min_pressure'),
                        max_humidity=row.get('max_humidity'),
                        max_precipitation=row.get('max_precipitation'),
                        max_wind_speed=row.get('max_wind_speed'),
                        description=row.get('description'),
                        status=1
                    )
                    session.add(extreme_event)
                    stored_count += 1
            
            # 提交事务
            session.commit()
            session.close()
            
            logger.info(f"极端天气事件数据存储完成，新增: {stored_count}条")
            return True, stored_count
        except IntegrityError as e:
            logger.error(f"极端天气事件数据存储失败，完整性错误: {e}")
            session.rollback()
            session.close()
            return False, 0
        except Exception as e:
            logger.error(f"极端天气事件数据存储失败: {e}")
            session.rollback()
            session.close()
            return False, 0
    
    def store_cleaning_logs(self, logs):
        """存储数据清洗日志"""
        try:
            session = self.db_manager.get_session()
            stored_count = 0
            
            for log in logs:
                # 插入日志数据
                cleaning_log = DataCleaningLog(
                    process_time=log['process_time'],
                    data_source=log['data_source'],
                    field_name=log['field_name'],
                    process_type=log['process_type'],
                    process_method=log['process_method'],
                    before_count=log['before_count'],
                    after_count=log['after_count'],
                    affected_count=log['affected_count'],
                    description=log['description']
                )
                session.add(cleaning_log)
                stored_count += 1
            
            # 提交事务
            session.commit()
            session.close()
            
            logger.info(f"数据清洗日志存储完成，新增: {stored_count}条")
            return True, stored_count
        except Exception as e:
            logger.error(f"数据清洗日志存储失败: {e}")
            session.rollback()
            session.close()
            return False, 0
    
    def preprocess_and_store(self, df, data_type='historical'):
        """预处理并存储数据"""
        try:
            # 1. 数据预处理
            processed_df = self.preprocessor.preprocess_data(df, data_type)
            
            if processed_df is None:
                logger.error("数据预处理失败，无法存储")
                return False, 0, 0
            
            # 2. 存储清洗日志
            if self.preprocessor.cleaning_logs:
                self.store_cleaning_logs(self.preprocessor.cleaning_logs)
                # 清空日志列表
                self.preprocessor.cleaning_logs = []
            
            # 3. 根据数据类型存储
            if data_type == 'realtime':
                success, stored, updated = self.store_realtime_weather(processed_df)
                return success, stored, updated
            elif data_type == 'historical':
                success, stored = self.store_historical_weather(processed_df)
                return success, stored, 0
            elif data_type == 'extreme':
                success, stored = self.store_extreme_events(processed_df)
                return success, stored, 0
            else:
                logger.error(f"不支持的数据类型: {data_type}")
                return False, 0, 0
        except Exception as e:
            logger.error(f"预处理并存储数据失败: {e}")
            return False, 0, 0
    
    def load_historical_data_from_csv(self, file_path, data_type='historical'):
        """从CSV文件加载历史数据并存储"""
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path)
            logger.info(f"从文件 {file_path} 读取了 {len(df)} 条数据")
            
            # 预处理并存储
            return self.preprocess_and_store(df, data_type)
        except Exception as e:
            logger.error(f"从CSV文件加载历史数据失败: {e}")
            return False, 0, 0
    
    def bulk_load_historical_data(self, directory_path, data_type='historical'):
        """批量加载目录下的所有CSV文件"""
        try:
            total_stored = 0
            total_updated = 0
            
            # 遍历目录下的所有CSV文件
            for filename in os.listdir(directory_path):
                if filename.endswith('.csv'):
                    file_path = os.path.join(directory_path, filename)
                    logger.info(f"开始处理文件: {filename}")
                    success, stored, updated = self.load_historical_data_from_csv(file_path, data_type)
                    if success:
                        total_stored += stored
                        total_updated += updated
            
            logger.info(f"批量加载完成，总共新增: {total_stored}条，更新: {total_updated}条")
            return True, total_stored, total_updated
        except Exception as e:
            logger.error(f"批量加载历史数据失败: {e}")
            return False, 0, 0
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close()

if __name__ == "__main__":
    # 示例用法
    import pandas as pd
    from datetime import datetime, timedelta
    
    # 创建示例数据
    dates = [datetime.now() - timedelta(hours=i) for i in range(10)]
    data = {
        'timestamp': dates,
        'city': ['beijing'] * 10,
        'temperature': [20 + i * 0.5 for i in range(10)],
        'pressure': [1013 + i * 0.2 for i in range(10)],
        'humidity': [60 + i * 1 for i in range(10)],
        'precipitation': [i * 0.1 for i in range(10)],
        'wind_speed': [5 + i * 0.3 for i in range(10)],
        'wind_direction': [i * 36 for i in range(10)],
        'source': ['Meteostat'] * 10
    }
    
    df = pd.DataFrame(data)
    
    # 创建存储实例
    storage = WeatherDataStorage()
    
    # 初始化数据库
    storage.db_manager.init_database()
    
    # 预处理并存储数据
    success, stored, updated = storage.preprocess_and_store(df, data_type='historical')
    
    if success:
        logger.info(f"示例数据存储成功，新增: {stored}条，更新: {updated}条")
    else:
        logger.error("示例数据存储失败")
    
    # 关闭连接
    storage.close()
