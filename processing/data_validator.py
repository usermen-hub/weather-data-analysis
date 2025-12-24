import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherDataValidator:
    def __init__(self):
        # 数据质量规则
        self.validation_rules = {
            'temperature': {'min': -50, 'max': 60, 'unit': '°C'},
            'pressure': {'min': 800, 'max': 1200, 'unit': 'hPa'},
            'humidity': {'min': 0, 'max': 100, 'unit': '%'},
            'precipitation': {'min': 0, 'max': 500, 'unit': 'mm'},
            'wind_speed': {'min': 0, 'max': 100, 'unit': 'm/s'},
            'wind_direction': {'min': 0, 'max': 360, 'unit': '°'}
        }
        
        # 数据类型映射
        self.data_types = {
            'timestamp': 'datetime64[ns]',
            'city': 'object',
            'temperature': 'float64',
            'pressure': 'float64',
            'humidity': 'float64',
            'precipitation': 'float64',
            'wind_speed': 'float64',
            'wind_direction': 'float64',
            'source': 'object'
        }
    
    def validate_data_format(self, data):
        """验证数据格式规范性"""
        try:
            # 检查必需字段
            required_fields = ['timestamp', 'city', 'temperature', 'pressure', 'humidity', 
                              'precipitation', 'wind_speed', 'wind_direction', 'source']
            
            if isinstance(data, dict):
                # 实时数据验证
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    logger.error(f"缺少必需字段: {missing_fields}")
                    return False, f"缺少必需字段: {missing_fields}"
            elif isinstance(data, pd.DataFrame):
                # 历史数据验证
                missing_fields = [field for field in required_fields if field not in data.columns]
                if missing_fields:
                    logger.error(f"缺少必需字段: {missing_fields}")
                    return False, f"缺少必需字段: {missing_fields}"
            else:
                logger.error(f"数据格式错误，应为dict或DataFrame，实际为{type(data)}")
                return False, f"数据格式错误，应为dict或DataFrame，实际为{type(data)}"
            
            logger.info("数据格式验证通过")
            return True, "数据格式验证通过"
            
        except Exception as e:
            logger.error(f"数据格式验证失败: {e}")
            return False, str(e)
    
    def validate_data_range(self, data):
        """验证数据取值范围"""
        try:
            if isinstance(data, dict):
                # 实时数据范围验证
                for field, rules in self.validation_rules.items():
                    if field in data:
                        value = data[field]
                        if not (rules['min'] <= value <= rules['max']):
                            logger.warning(f"{field} 值 {value} 超出有效范围 [{rules['min']}, {rules['max']}]")
                            return False, f"{field} 值 {value} 超出有效范围 [{rules['min']}, {rules['max']}]"
            elif isinstance(data, pd.DataFrame):
                # 历史数据范围验证
                for field, rules in self.validation_rules.items():
                    if field in data.columns:
                        # 检查超出范围的值
                        out_of_range = data[(data[field] < rules['min']) | (data[field] > rules['max'])]
                        if not out_of_range.empty:
                            logger.warning(f"{field} 有 {len(out_of_range)} 条记录超出有效范围 [{rules['min']}, {rules['max']}]")
                            # 替换为NaN
                            data.loc[(data[field] < rules['min']) | (data[field] > rules['max']), field] = np.nan
            
            logger.info("数据范围验证通过")
            return True, "数据范围验证通过"
            
        except Exception as e:
            logger.error(f"数据范围验证失败: {e}")
            return False, str(e)
    
    def standardize_data(self, data):
        """标准化数据格式与单位"""
        try:
            if isinstance(data, dict):
                # 转换为DataFrame进行标准化
                df = pd.DataFrame([data])
            else:
                df = data.copy()
            
            # 转换数据类型
            for col, dtype in self.data_types.items():
                if col in df.columns:
                    if dtype == 'datetime64[ns]':
                        df[col] = pd.to_datetime(df[col])
                    else:
                        df[col] = df[col].astype(dtype)
            
            # 处理缺失值
            df = df.ffill().bfill()
            
            # 确保所有数值列都是正数（根据实际情况调整）
            for field in ['pressure', 'humidity', 'precipitation', 'wind_speed']:
                if field in df.columns:
                    df[field] = df[field].clip(lower=0)
            
            # 风向标准化到0-360度
            if 'wind_direction' in df.columns:
                df['wind_direction'] = df['wind_direction'] % 360
            
            logger.info("数据标准化完成")
            return df
            
        except Exception as e:
            logger.error(f"数据标准化失败: {e}")
            return None
    
    def generate_data_dictionary(self, output_path='./docs'):
        """生成数据字典"""
        try:
            # 确保输出目录存在
            os.makedirs(output_path, exist_ok=True)
            
            # 数据字典内容
            data_dict = {
                '数据集描述': '气象数据包含实时和历史的气温、气压、湿度、降水量、风速、风向等核心指标',
                '数据来源': ['OpenWeatherMap', 'Meteostat', 'Kaggle极端天气数据集'],
                '字段信息': {
                    'timestamp': {'描述': '数据采集时间', '数据类型': 'datetime64[ns]', '格式': 'YYYY-MM-DD HH:MM:SS'},
                    'city': {'描述': '城市名称', '数据类型': 'string', '取值范围': ['beijing', 'shanghai', 'guangzhou', 'shenzhen', 'chengdu']},
                    'temperature': {'描述': '气温', '数据类型': 'float64', '单位': '°C', '取值范围': [-50, 60]},
                    'pressure': {'描述': '气压', '数据类型': 'float64', '单位': 'hPa', '取值范围': [800, 1200]},
                    'humidity': {'描述': '湿度', '数据类型': 'float64', '单位': '%', '取值范围': [0, 100]},
                    'precipitation': {'描述': '降水量', '数据类型': 'float64', '单位': 'mm', '取值范围': [0, 500]},
                    'wind_speed': {'描述': '风速', '数据类型': 'float64', '单位': 'm/s', '取值范围': [0, 100]},
                    'wind_direction': {'描述': '风向', '数据类型': 'float64', '单位': '°', '取值范围': [0, 360]},
                    'source': {'描述': '数据来源', '数据类型': 'string', '取值范围': ['OpenWeatherMap', 'Meteostat', 'Kaggle']}
                },
                '更新频率': '实时数据每小时更新一次，历史数据按需获取',
                '数据质量': '经过格式验证、范围验证和标准化处理'
            }
            
            # 保存为JSON文件
            import json
            with open(f'{output_path}/data_dictionary.json', 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
            
            # 保存为Markdown文件，方便阅读
            with open(f'{output_path}/data_dictionary.md', 'w', encoding='utf-8') as f:
                f.write('# 气象数据字典\n\n')
                f.write('## 数据集描述\n')
                f.write(f'{data_dict["数据集描述"]}\n\n')
                f.write('## 数据来源\n')
                for source in data_dict["数据来源"]:
                    f.write(f'- {source}\n')
                f.write('\n## 字段信息\n')
                f.write('| 字段名 | 描述 | 数据类型 | 单位 | 取值范围 | 格式 |\n')
                f.write('| --- | --- | --- | --- | --- | --- |\n')
                
                for field, info in data_dict["字段信息"].items():
                    unit = info.get("单位", "-")
                    range_val = info.get("取值范围", "-")
                    format_val = info.get("格式", "-")
                    f.write(f'| {field} | {info["描述"]} | {info["数据类型"]} | {unit} | {range_val} | {format_val} |\n')
                
                f.write('\n## 更新频率\n')
                f.write(f'{data_dict["更新频率"]}\n\n')
                f.write('## 数据质量\n')
                f.write(f'{data_dict["数据质量"]}\n')
            
            logger.info(f"数据字典已生成到 {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"生成数据字典失败: {e}")
            return False
    
    def validate_and_standardize(self, data):
        """完整的数据验证和标准化流程"""
        try:
            # 1. 格式验证
            format_valid, format_msg = self.validate_data_format(data)
            if not format_valid:
                return None, format_msg
            
            # 2. 范围验证
            range_valid, range_msg = self.validate_data_range(data)
            if not range_valid:
                return None, range_msg
            
            # 3. 标准化
            standardized_data = self.standardize_data(data)
            if standardized_data is None:
                return None, "数据标准化失败"
            
            logger.info("数据验证和标准化流程完成")
            return standardized_data, "数据验证和标准化流程完成"
            
        except Exception as e:
            logger.error(f"数据验证和标准化流程失败: {e}")
            return None, str(e)
    
    def process_kaggle_dataset(self, input_path='./data', output_path='./data/processed'):
        """处理Kaggle极端天气数据集"""
        try:
            # 确保输出目录存在
            os.makedirs(output_path, exist_ok=True)
            
            # 遍历所有CSV文件
            for filename in os.listdir(input_path):
                if filename.endswith('.csv') and 'extreme' in filename.lower():
                    file_path = os.path.join(input_path, filename)
                    logger.info(f"处理Kaggle数据集: {filename}")
                    
                    # 读取数据
                    df = pd.read_csv(file_path)
                    
                    # 根据Kaggle数据集的实际字段名进行映射和处理
                    # 这里需要根据实际下载的数据集结构进行调整
                    # 示例映射（需要根据实际数据集调整）
                    column_mapping = {
                        'datetime': 'timestamp',
                        'city_name': 'city',
                        'temp': 'temperature',
                        'pressure': 'pressure',
                        'humidity': 'humidity',
                        'precip': 'precipitation',
                        'wind_speed': 'wind_speed',
                        'wind_deg': 'wind_direction'
                    }
                    
                    # 重命名列
                    df = df.rename(columns=column_mapping)
                    
                    # 添加数据源
                    df['source'] = 'Kaggle'
                    
                    # 验证和标准化
                    standardized_df, msg = self.validate_and_standardize(df)
                    if standardized_df is not None:
                        # 保存处理后的数据
                        output_file = os.path.join(output_path, f'processed_{filename}')
                        standardized_df.to_csv(output_file, index=False)
                        logger.info(f"Kaggle数据集处理完成，保存到: {output_file}")
            
            logger.info("所有Kaggle数据集处理完成")
            return True
            
        except Exception as e:
            logger.error(f"处理Kaggle数据集失败: {e}")
            return False

if __name__ == "__main__":
    validator = WeatherDataValidator()
    
    # 生成数据字典
    validator.generate_data_dictionary()
    
    # 示例数据验证
    sample_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'city': 'beijing',
        'temperature': 25.5,
        'pressure': 1013.25,
        'humidity': 60,
        'precipitation': 0,
        'wind_speed': 5.5,
        'wind_direction': 180,
        'source': 'Test'
    }
    
    standardized_data, msg = validator.validate_and_standardize(sample_data)
    if standardized_data is not None:
        logger.info(f"示例数据验证和标准化成功: {msg}")
        print(standardized_data)