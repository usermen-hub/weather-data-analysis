import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, DECIMAL, ForeignKey, Index, BigInteger, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 创建基类
Base = declarative_base()

# 城市表
class City(Base):
    __tablename__ = 'cities'
    
    city_id = Column(Integer, primary_key=True, autoincrement=True)
    city_name = Column(String(50), unique=True, nullable=False, comment='城市名称')
    city_code = Column(String(20), nullable=False, comment='城市编码')
    latitude = Column(DECIMAL(10, 6), nullable=False, comment='纬度')
    longitude = Column(DECIMAL(10, 6), nullable=False, comment='经度')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    real_time_weathers = relationship('RealTimeWeather', back_populates='city')
    historical_weathers = relationship('HistoricalWeather', back_populates='city')
    extreme_events = relationship('ExtremeEvent', back_populates='city')
    
    def __repr__(self):
        return f"<City(city_id={self.city_id}, city_name='{self.city_name}')>"

# 数据源表
class DataSource(Base):
    __tablename__ = 'data_sources'
    
    source_id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(100), unique=True, nullable=False, comment='数据源名称')
    source_code = Column(String(20), nullable=False, comment='数据源编码')
    description = Column(Text, comment='数据源描述')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    real_time_weathers = relationship('RealTimeWeather', back_populates='data_source')
    historical_weathers = relationship('HistoricalWeather', back_populates='data_source')
    extreme_events = relationship('ExtremeEvent', back_populates='data_source')
    
    def __repr__(self):
        return f"<DataSource(source_id={self.source_id}, source_name='{self.source_name}')>"

# 实时数据表
class RealTimeWeather(Base):
    __tablename__ = 'real_time_weather'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey('cities.city_id'), nullable=False, comment='城市ID')
    source_id = Column(Integer, ForeignKey('data_sources.source_id'), nullable=False, comment='数据源ID')
    timestamp = Column(DateTime, nullable=False, comment='数据采集时间')
    temperature = Column(DECIMAL(5, 2), comment='气温（°C）')
    pressure = Column(DECIMAL(6, 2), comment='气压（hPa）')
    humidity = Column(DECIMAL(5, 2), comment='湿度（%）')
    precipitation = Column(DECIMAL(6, 2), comment='降水量（mm）')
    wind_speed = Column(DECIMAL(5, 2), comment='风速（m/s）')
    wind_direction = Column(DECIMAL(5, 2), comment='风向（°）')
    status = Column(SmallInteger, default=1, comment='数据状态（0:无效, 1:有效）')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    city = relationship('City', back_populates='real_time_weathers')
    data_source = relationship('DataSource', back_populates='real_time_weathers')
    
    # 索引
    __table_args__ = (
        Index('idx_city_timestamp', 'city_id', 'timestamp', unique=True),
    )
    
    def __repr__(self):
        return f"<RealTimeWeather(id={self.id}, city_id={self.city_id}, timestamp={self.timestamp})>"

# 历史数据表
class HistoricalWeather(Base):
    __tablename__ = 'historical_weather'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey('cities.city_id'), nullable=False, comment='城市ID')
    source_id = Column(Integer, ForeignKey('data_sources.source_id'), nullable=False, comment='数据源ID')
    timestamp = Column(DateTime, nullable=False, comment='数据采集时间')
    temperature = Column(DECIMAL(5, 2), comment='气温（°C）')
    pressure = Column(DECIMAL(6, 2), comment='气压（hPa）')
    humidity = Column(DECIMAL(5, 2), comment='湿度（%）')
    precipitation = Column(DECIMAL(6, 2), comment='降水量（mm）')
    wind_speed = Column(DECIMAL(5, 2), comment='风速（m/s）')
    wind_direction = Column(DECIMAL(5, 2), comment='风向（°）')
    status = Column(SmallInteger, default=1, comment='数据状态（0:无效, 1:有效）')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    city = relationship('City', back_populates='historical_weathers')
    data_source = relationship('DataSource', back_populates='historical_weathers')
    
    # 索引
    __table_args__ = (
        Index('idx_city_timestamp_hist', 'city_id', 'timestamp', unique=True),
        Index('idx_timestamp_hist', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<HistoricalWeather(id={self.id}, city_id={self.city_id}, timestamp={self.timestamp})>"

# 极端事件数据表
class ExtremeEvent(Base):
    __tablename__ = 'extreme_events'
    
    event_id = Column(BigInteger, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey('cities.city_id'), nullable=False, comment='城市ID')
    source_id = Column(Integer, ForeignKey('data_sources.source_id'), nullable=False, comment='数据源ID')
    event_type = Column(String(50), nullable=False, comment='事件类型（暴雨、高温、大风等）')
    event_level = Column(SmallInteger, nullable=False, comment='事件等级（1-5级）')
    start_time = Column(DateTime, nullable=False, comment='事件开始时间')
    end_time = Column(DateTime, nullable=False, comment='事件结束时间')
    max_temperature = Column(DECIMAL(5, 2), comment='最大气温（°C）')
    min_temperature = Column(DECIMAL(5, 2), comment='最小气温（°C）')
    max_pressure = Column(DECIMAL(6, 2), comment='最大气压（hPa）')
    min_pressure = Column(DECIMAL(6, 2), comment='最小气压（hPa）')
    max_humidity = Column(DECIMAL(5, 2), comment='最大湿度（%）')
    max_precipitation = Column(DECIMAL(6, 2), comment='最大降水量（mm）')
    max_wind_speed = Column(DECIMAL(5, 2), comment='最大风速（m/s）')
    description = Column(Text, comment='事件描述')
    status = Column(SmallInteger, default=1, comment='数据状态（0:无效, 1:有效）')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    city = relationship('City', back_populates='extreme_events')
    data_source = relationship('DataSource', back_populates='extreme_events')
    
    # 索引
    __table_args__ = (
        Index('idx_city_event', 'city_id', 'event_type', 'start_time'),
        Index('idx_event_time', 'start_time', 'end_time'),
    )
    
    def __repr__(self):
        return f"<ExtremeEvent(event_id={self.event_id}, event_type='{self.event_type}', city_id={self.city_id})>"

# 数据清洗日志表
class DataCleaningLog(Base):
    __tablename__ = 'data_cleaning_logs'
    
    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    process_time = Column(DateTime, nullable=False, comment='处理时间')
    data_source = Column(String(100), nullable=False, comment='数据源')
    field_name = Column(String(50), nullable=False, comment='字段名')
    process_type = Column(String(50), nullable=False, comment='处理类型（异常值检测/缺失值处理）')
    process_method = Column(String(100), nullable=False, comment='处理方法')
    before_count = Column(Integer, nullable=False, comment='处理前数量')
    after_count = Column(Integer, nullable=False, comment='处理后数量')
    affected_count = Column(Integer, nullable=False, comment='受影响数量')
    description = Column(Text, comment='处理描述')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    
    def __repr__(self):
        return f"<DataCleaningLog(log_id={self.log_id}, process_time={self.process_time}, field_name='{self.field_name}')>"

class DatabaseManager:
    def __init__(self):
        # 从环境变量获取数据库连接信息
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '3306')
        self.db_name = os.getenv('DB_NAME', 'weather_data')
        self.db_user = os.getenv('DB_USER', 'root')
        self.db_password = os.getenv('DB_PASSWORD', '')
        
        # 构建数据库连接URL
        self.db_url = f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        
        # 创建数据库引擎
        self.engine = create_engine(self.db_url, echo=False)
        
        # 创建会话工厂
        self.Session = sessionmaker(bind=self.engine)
    
    def create_database(self):
        """创建数据库（如果不存在）"""
        try:
            # 创建临时引擎，不指定数据库
            temp_url = f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}?charset=utf8mb4"
            temp_engine = create_engine(temp_url, echo=False)
            
            from sqlalchemy import text
            
            with temp_engine.connect() as conn:
                # 检查数据库是否存在
                result = conn.execute(text(f"SHOW DATABASES LIKE '{self.db_name}'"))
                if not result.fetchone():
                    # 创建数据库
                    conn.execute(text(f"CREATE DATABASE {self.db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                    logger.info(f"数据库 {self.db_name} 创建成功")
                else:
                    logger.info(f"数据库 {self.db_name} 已存在")
            
            # 关闭临时引擎
            temp_engine.dispose()
            return True
        except Exception as e:
            logger.error(f"创建数据库失败: {e}")
            return False
    
    def create_tables(self):
        """创建所有表"""
        try:
            # 创建所有表
            Base.metadata.create_all(self.engine)
            logger.info("所有表创建成功")
            return True
        except Exception as e:
            logger.error(f"创建表失败: {e}")
            return False
    
    def init_database(self):
        """初始化数据库，包括创建数据库和表"""
        try:
            # 创建数据库
            self.create_database()
            
            # 创建表
            self.create_tables()
            
            # 初始化基础数据
            self.init_base_data()
            
            logger.info("数据库初始化完成")
            return True
        except Exception as e:
            logger.error(f"初始化数据库失败: {e}")
            return False
    
    def init_base_data(self):
        """初始化基础数据，如城市、数据源等"""
        try:
            session = self.Session()
            
            # 初始化城市数据
            cities_data = [
                {'city_name': 'beijing', 'city_code': 'BJ', 'latitude': 39.9042, 'longitude': 116.4074},
                {'city_name': 'shanghai', 'city_code': 'SH', 'latitude': 31.2304, 'longitude': 121.4737},
                {'city_name': 'guangzhou', 'city_code': 'GZ', 'latitude': 23.1291, 'longitude': 113.2644},
                {'city_name': 'shenzhen', 'city_code': 'SZ', 'latitude': 22.5431, 'longitude': 114.0579},
                {'city_name': 'chengdu', 'city_code': 'CD', 'latitude': 30.5728, 'longitude': 104.0668}
            ]
            
            for city_data in cities_data:
                # 检查城市是否已存在
                existing_city = session.query(City).filter_by(city_name=city_data['city_name']).first()
                if not existing_city:
                    city = City(**city_data)
                    session.add(city)
                    logger.info(f"添加城市: {city_data['city_name']}")
            
            # 初始化数据源数据
            data_sources_data = [
                {'source_name': 'OpenWeatherMap', 'source_code': 'OWM', 'description': '全球气象数据服务'},
                {'source_name': 'Meteostat', 'source_code': 'MS', 'description': '开源气象数据平台'},
                {'source_name': 'Kaggle', 'source_code': 'KG', 'description': '极端天气数据集'}
            ]
            
            for source_data in data_sources_data:
                # 检查数据源是否已存在
                existing_source = session.query(DataSource).filter_by(source_name=source_data['source_name']).first()
                if not existing_source:
                    data_source = DataSource(**source_data)
                    session.add(data_source)
                    logger.info(f"添加数据源: {source_data['source_name']}")
            
            # 提交事务
            session.commit()
            session.close()
            
            logger.info("基础数据初始化完成")
            return True
        except Exception as e:
            logger.error(f"初始化基础数据失败: {e}")
            session.rollback()
            session.close()
            return False
    
    def get_session(self):
        """获取数据库会话"""
        return self.Session()
    
    def close(self):
        """关闭数据库连接"""
        self.engine.dispose()
        logger.info("数据库连接已关闭")

if __name__ == "__main__":
    # 示例用法
    db_manager = DatabaseManager()
    
    # 初始化数据库
    if db_manager.init_database():
        logger.info("数据库初始化成功")
    else:
        logger.error("数据库初始化失败")
    
    # 关闭数据库连接
    db_manager.close()
