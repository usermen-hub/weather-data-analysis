import os
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processing.data_storage import WeatherDataStorage

def main():
    """加载、清洗并存储CSV数据到数据库"""
    logger.info("=== 开始处理CSV数据 ===")
    
    # 数据目录
    data_dir = "d:\code\weather_data\data"
    
    # 检查数据目录是否存在
    if not os.path.exists(data_dir):
        logger.error(f"数据目录不存在: {data_dir}")
        return 1
    
    # 创建存储实例
    storage = WeatherDataStorage()
    
    # 获取所有CSV文件
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        logger.error(f"数据目录中没有找到CSV文件: {data_dir}")
        storage.close()
        return 1
    
    logger.info(f"找到 {len(csv_files)} 个CSV文件")
    
    # 处理每个CSV文件
    for csv_file in csv_files:
        file_path = os.path.join(data_dir, csv_file)
        logger.info(f"开始处理文件: {csv_file}")
        
        # 判断数据类型
        data_type = 'historical'  # 默认是历史数据
        if 'realtime' in csv_file.lower():
            data_type = 'realtime'
        elif 'extreme' in csv_file.lower():
            data_type = 'extreme'
        
        # 加载并存储数据
        success, stored, updated = storage.load_historical_data_from_csv(file_path, data_type)
        
        if success:
            logger.info(f"文件 {csv_file} 处理成功，新增: {stored}条，更新: {updated}条")
        else:
            logger.error(f"文件 {csv_file} 处理失败")
    
    # 关闭资源
    storage.close()
    logger.info("=== 所有CSV数据处理完成 ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())