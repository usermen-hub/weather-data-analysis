import os
import sys
import logging
import pandas as pd
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入模块
from processing.data_preprocessor import WeatherDataPreprocessor
from processing.database_manager import DatabaseManager
from processing.data_storage import WeatherDataStorage

def test_data_preprocessing():
    """测试数据预处理功能"""
    logger.info("=== 开始测试数据预处理功能 ===")
    
    try:
        # 创建示例数据
        dates = [datetime.now() - timedelta(hours=i) for i in range(100)]
        data = {
            'timestamp': dates,
            'city': ['beijing'] * 100,
            'temperature': [20 + i * 0.5 for i in range(100)],
            'pressure': [1013 + i * 0.2 for i in range(100)],
            'humidity': [60 + i * 1 for i in range(100)],
            'precipitation': [i * 0.1 for i in range(100)],
            'wind_speed': [5 + i * 0.3 for i in range(100)],
            'wind_direction': [i * 3.6 for i in range(100)],
            'source': ['Meteostat'] * 100
        }
        
        # 添加一些异常值
        data['temperature'][10] = 100  # 异常高温
        data['pressure'][20] = 1500     # 异常高压
        data['humidity'][30] = 150      # 异常高湿度
        
        # 添加一些缺失值
        data['temperature'][40] = None
        data['pressure'][50] = None
        data['humidity'][60] = None
        
        df = pd.DataFrame(data)
        logger.info(f"创建了 {len(df)} 条测试数据")
        
        # 创建预处理实例
        preprocessor = WeatherDataPreprocessor()
        
        # 执行预处理
        processed_df = preprocessor.preprocess_data(df, data_type='historical')
        
        if processed_df is not None:
            logger.info(f"数据预处理成功，处理后数据形状: {processed_df.shape}")
            logger.info("数据预处理测试通过")
            return True, processed_df
        else:
            logger.error("数据预处理失败")
            return False, None
    except Exception as e:
        logger.error(f"数据预处理测试失败: {e}", exc_info=True)
        return False, None

def test_database_init():
    """测试数据库初始化功能"""
    logger.info("=== 开始测试数据库初始化功能 ===")
    
    try:
        # 创建数据库管理器实例
        db_manager = DatabaseManager()
        
        # 初始化数据库
        result = db_manager.init_database()
        
        if result:
            logger.info("数据库初始化测试通过")
            return True, db_manager
        else:
            logger.error("数据库初始化失败")
            return False, None
    except Exception as e:
        logger.error(f"数据库初始化测试失败: {e}", exc_info=True)
        return False, None

def test_data_storage():
    """测试数据存储功能"""
    logger.info("=== 开始测试数据存储功能 ===")
    
    try:
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
        logger.info(f"创建了 {len(df)} 条测试数据")
        
        # 创建存储实例
        storage = WeatherDataStorage()
        
        # 测试预处理并存储
        success, stored, updated = storage.preprocess_and_store(df, data_type='historical')
        
        if success:
            logger.info(f"数据存储成功，新增: {stored}条，更新: {updated}条")
            logger.info("数据存储测试通过")
            return True, storage
        else:
            logger.error("数据存储失败")
            return False, None
    except Exception as e:
        logger.error(f"数据存储测试失败: {e}", exc_info=True)
        return False, None

def main():
    """主测试函数"""
    logger.info("=== 开始系统测试 ===")
    
    # 测试数据预处理
    preprocess_success, processed_df = test_data_preprocessing()
    
    # 测试数据库初始化
    db_success, db_manager = test_database_init()
    
    # 测试数据存储
    storage_success, storage = test_data_storage()
    
    # 关闭资源
    if 'db_manager' in locals() and db_manager:
        db_manager.close()
    if 'storage' in locals() and storage:
        storage.close()
    
    # 输出测试结果
    logger.info("=== 系统测试结果 ===")
    logger.info(f"数据预处理测试: {'通过' if preprocess_success else '失败'}")
    logger.info(f"数据库初始化测试: {'通过' if db_success else '失败'}")
    logger.info(f"数据存储测试: {'通过' if storage_success else '失败'}")
    
    if preprocess_success and db_success and storage_success:
        logger.info("所有测试通过，系统功能正常")
        return 0
    else:
        logger.error("部分测试失败，系统功能存在问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
