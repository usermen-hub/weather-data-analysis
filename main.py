import os
import sys
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_sources.data_collector import WeatherDataCollector
from processing.data_validator import WeatherDataValidator

def main():
    """主函数，整合数据采集、处理和API启动"""
    try:
        logger.info("=== 气象数据处理系统启动 ===")
        
        # 1. 初始化组件
        collector = WeatherDataCollector()
        validator = WeatherDataValidator()
        
        # 2. 生成数据字典
        logger.info("生成数据字典...")
        validator.generate_data_dictionary()
        
        # 3. 数据采集
        cities = ['beijing', 'shanghai', 'guangzhou', 'shenzhen', 'chengdu']
        
        for city in cities:
            # 获取实时数据
            logger.info(f"获取{city}实时气象数据...")
            realtime_data = collector.get_realtime_weather(city)
            if realtime_data:
                # 验证和标准化
                standardized_data, msg = validator.validate_and_standardize(realtime_data)
                if standardized_data is not None:
                    collector.save_data(realtime_data, f'realtime_weather_{city}_{datetime.now().strftime("%Y%m%d_%H%M%S")}', 'realtime')
            
            # 获取历史数据
            logger.info(f"获取{city}历史气象数据...")
            historical_data = collector.get_historical_weather(city)
            if historical_data is not None:
                # 验证和标准化
                standardized_data, msg = validator.validate_and_standardize(historical_data)
                if standardized_data is not None:
                    collector.save_data(standardized_data, f'historical_weather_{city}_{datetime.now().strftime("%Y%m%d")}', 'historical')
        
        # 4. 下载Kaggle数据集
        logger.info("下载Kaggle极端天气数据集...")
        collector.download_kaggle_dataset()
        
        # 5. 处理Kaggle数据集
        logger.info("处理Kaggle极端天气数据集...")
        validator.process_kaggle_dataset()
        
        logger.info("=== 气象数据处理系统执行完成 ===")
        logger.info("请运行 'python api/app.py' 启动数据查询API")
        
    except Exception as e:
        logger.error(f"系统执行失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()