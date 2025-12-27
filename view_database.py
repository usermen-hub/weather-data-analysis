import os
import sys
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processing.database_manager import DatabaseManager, HistoricalWeather, RealTimeWeather, ExtremeEvent, City, DataSource

def view_table_data(session, table_name, limit=10):
    """查看指定表的数据"""
    try:
        if table_name == 'cities':
            data = session.query(City).limit(limit).all()
            print(f"\n=== 城市表数据 (前{limit}条) ===")
            for city in data:
                print(f"ID: {city.city_id}, 名称: {city.city_name}, 编码: {city.city_code}, 纬度: {city.latitude}, 经度: {city.longitude}")
        
        elif table_name == 'data_sources':
            data = session.query(DataSource).limit(limit).all()
            print(f"\n=== 数据源表数据 (前{limit}条) ===")
            for source in data:
                print(f"ID: {source.source_id}, 名称: {source.source_name}, 编码: {source.source_code}")
        
        elif table_name == 'historical_weather':
            data = session.query(HistoricalWeather).order_by(HistoricalWeather.timestamp.desc()).limit(limit).all()
            print(f"\n=== 历史天气数据表数据 (前{limit}条，按时间倒序) ===")
            for weather in data:
                print(f"ID: {weather.id}, 城市ID: {weather.city_id}, 数据源ID: {weather.source_id}, 时间: {weather.timestamp}, 温度: {weather.temperature}°C, 湿度: {weather.humidity}%, 风速: {weather.wind_speed}m/s")
        
        elif table_name == 'real_time_weather':
            data = session.query(RealTimeWeather).order_by(RealTimeWeather.timestamp.desc()).limit(limit).all()
            print(f"\n=== 实时天气数据表数据 (前{limit}条，按时间倒序) ===")
            for weather in data:
                print(f"ID: {weather.id}, 城市ID: {weather.city_id}, 数据源ID: {weather.source_id}, 时间: {weather.timestamp}, 温度: {weather.temperature}°C, 湿度: {weather.humidity}%, 风速: {weather.wind_speed}m/s")
        
        elif table_name == 'extreme_events':
            data = session.query(ExtremeEvent).order_by(ExtremeEvent.start_time.desc()).limit(limit).all()
            print(f"\n=== 极端事件数据表数据 (前{limit}条，按时间倒序) ===")
            for event in data:
                print(f"ID: {event.event_id}, 城市ID: {event.city_id}, 类型: {event.event_type}, 等级: {event.event_level}, 开始时间: {event.start_time}, 结束时间: {event.end_time}")
        
        else:
            print(f"\n表名 {table_name} 不存在")
            return False
        
        return True
    except Exception as e:
        logger.error(f"查看表数据失败: {e}")
        return False

def view_historical_data_by_city(session, city_name, limit=10):
    """查看特定城市的历史天气数据"""
    try:
        # 获取城市ID
        city = session.query(City).filter(City.city_name == city_name).first()
        if not city:
            print(f"\n城市 {city_name} 不存在")
            return False
        
        data = session.query(HistoricalWeather).filter(HistoricalWeather.city_id == city.city_id).order_by(HistoricalWeather.timestamp.desc()).limit(limit).all()
        print(f"\n=== {city_name} 历史天气数据 (前{limit}条，按时间倒序) ===")
        for weather in data:
            print(f"时间: {weather.timestamp}, 温度: {weather.temperature}°C, 气压: {weather.pressure}hPa, 湿度: {weather.humidity}%, 降水量: {weather.precipitation}mm, 风速: {weather.wind_speed}m/s, 风向: {weather.wind_direction}°")
        
        return True
    except Exception as e:
        logger.error(f"查看城市历史数据失败: {e}")
        return False

def get_table_counts(session):
    """获取各表的数据行数"""
    try:
        print("\n=== 数据库表数据统计 ===")
        
        # 城市表
        city_count = session.query(City).count()
        print(f"城市表: {city_count} 条记录")
        
        # 数据源表
        source_count = session.query(DataSource).count()
        print(f"数据源表: {source_count} 条记录")
        
        # 历史天气表
        historical_count = session.query(HistoricalWeather).count()
        print(f"历史天气表: {historical_count} 条记录")
        
        # 实时天气表
        realtime_count = session.query(RealTimeWeather).count()
        print(f"实时天气表: {realtime_count} 条记录")
        
        # 极端事件表
        extreme_count = session.query(ExtremeEvent).count()
        print(f"极端事件表: {extreme_count} 条记录")
        
        return True
    except Exception as e:
        logger.error(f"获取表统计失败: {e}")
        return False

def main():
    """主函数"""
    print("=== 天气数据数据库查看工具 ===")
    
    # 创建数据库管理器
    db_manager = DatabaseManager()
    session = db_manager.get_session()
    
    try:
        while True:
            print("\n请选择要执行的操作:")
            print("1. 查看所有表的数据行数")
            print("2. 查看指定表的数据")
            print("3. 查看特定城市的历史天气数据")
            print("4. 退出")
            
            choice = input("\n请输入选项 (1-4): ")
            
            if choice == '1':
                get_table_counts(session)
            
            elif choice == '2':
                table_name = input("请输入表名 (cities/data_sources/historical_weather/real_time_weather/extreme_events): ")
                limit = input("请输入要显示的记录数 (默认10): ")
                limit = int(limit) if limit.isdigit() else 10
                view_table_data(session, table_name, limit)
            
            elif choice == '3':
                city_name = input("请输入城市名称 (beijing/shanghai/guangzhou/shenzhen/chengdu): ")
                limit = input("请输入要显示的记录数 (默认10): ")
                limit = int(limit) if limit.isdigit() else 10
                view_historical_data_by_city(session, city_name, limit)
            
            elif choice == '4':
                print("\n退出程序")
                break
            
            else:
                print("\n无效的选项，请重新输入")
    
    except KeyboardInterrupt:
        print("\n\n程序被中断")
    
    finally:
        # 关闭会话和数据库连接
        session.close()
        db_manager.close()

if __name__ == "__main__":
    main()
