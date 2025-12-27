import pandas as pd
import numpy as np
import logging
from datetime import datetime
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherDataPreprocessor:
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
        
        # 清洗日志列表
        self.cleaning_logs = []
    
    def detect_outliers_iqr(self, df, column):
        """使用IQR方法检测异常值"""
        try:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
            return outliers, lower_bound, upper_bound
        except Exception as e:
            logger.error(f"使用IQR方法检测{column}异常值失败: {e}")
            return pd.DataFrame(), None, None
    
    def detect_outliers_zscore(self, df, column, threshold=3):
        """使用Z-score方法检测异常值"""
        try:
            mean = df[column].mean()
            std = df[column].std()
            z_scores = (df[column] - mean) / std
            
            outliers = df[abs(z_scores) > threshold]
            return outliers
        except Exception as e:
            logger.error(f"使用Z-score方法检测{column}异常值失败: {e}")
            return pd.DataFrame()
    
    def detect_outliers_business(self, df, column):
        """基于业务规则检测异常值"""
        try:
            if column not in self.validation_rules:
                return pd.DataFrame()
            
            rules = self.validation_rules[column]
            outliers = df[(df[column] < rules['min']) | (df[column] > rules['max'])]
            return outliers
        except Exception as e:
            logger.error(f"基于业务规则检测{column}异常值失败: {e}")
            return pd.DataFrame()
    
    def handle_outliers(self, df, column, method='interpolate'):
        """处理异常值"""
        try:
            # 检测异常值
            iqr_outliers, _, _ = self.detect_outliers_iqr(df, column)
            business_outliers = self.detect_outliers_business(df, column)
            
            # 合并所有异常值（去重）
            outliers = pd.concat([iqr_outliers, business_outliers]).drop_duplicates()
            outlier_count = len(outliers)
            
            if outlier_count == 0:
                return df, 0
            
            # 记录日志
            self.cleaning_logs.append({
                'process_time': datetime.now(),
                'data_source': 'unknown',
                'field_name': column,
                'process_type': '异常值检测',
                'process_method': method,
                'before_count': len(df),
                'after_count': len(df) - outlier_count,
                'affected_count': outlier_count,
                'description': f"检测到{outlier_count}个异常值，使用{method}方法处理"
            })
            
            # 处理异常值
            df_copy = df.copy()
            
            if method == 'drop':
                # 删除异常值
                df_copy = df_copy.drop(outliers.index)
            elif method == 'mean':
                # 均值填充
                mean_val = df_copy[column].mean()
                df_copy.loc[outliers.index, column] = mean_val
            elif method == 'median':
                # 中位数填充
                median_val = df_copy[column].median()
                df_copy.loc[outliers.index, column] = median_val
            elif method == 'interpolate':
                # 线性插值
                # 先将异常值标记为NaN
                df_copy.loc[outliers.index, column] = np.nan
                # 然后进行线性插值
                df_copy[column] = df_copy[column].interpolate(method='linear')
            elif method == 'ffill':
                # 前向填充
                df_copy.loc[outliers.index, column] = np.nan
                df_copy[column] = df_copy[column].ffill()
            elif method == 'bfill':
                # 后向填充
                df_copy.loc[outliers.index, column] = np.nan
                df_copy[column] = df_copy[column].bfill()
            
            return df_copy, outlier_count
        except Exception as e:
            logger.error(f"处理{column}异常值失败: {e}")
            return df, 0
    
    def handle_missing_values(self, df, column, method='interpolate'):
        """处理缺失值"""
        try:
            # 统计缺失值数量
            missing_count = df[column].isnull().sum()
            
            if missing_count == 0:
                return df, 0
            
            # 记录日志
            self.cleaning_logs.append({
                'process_time': datetime.now(),
                'data_source': 'unknown',
                'field_name': column,
                'process_type': '缺失值处理',
                'process_method': method,
                'before_count': len(df),
                'after_count': len(df) - missing_count,
                'affected_count': missing_count,
                'description': f"检测到{missing_count}个缺失值，使用{method}方法处理"
            })
            
            # 处理缺失值
            df_copy = df.copy()
            
            if method == 'drop':
                # 删除缺失值
                df_copy = df_copy.dropna(subset=[column])
            elif method == 'mean':
                # 均值填充
                mean_val = df_copy[column].mean()
                df_copy[column] = df_copy[column].fillna(mean_val)
            elif method == 'median':
                # 中位数填充
                median_val = df_copy[column].median()
                df_copy[column] = df_copy[column].fillna(median_val)
            elif method == 'mode':
                # 众数填充
                mode_val = df_copy[column].mode()[0]
                df_copy[column] = df_copy[column].fillna(mode_val)
            elif method == 'interpolate':
                # 线性插值
                df_copy[column] = df_copy[column].interpolate(method='linear')
            elif method == 'ffill':
                # 前向填充
                df_copy[column] = df_copy[column].ffill()
            elif method == 'bfill':
                # 后向填充
                df_copy[column] = df_copy[column].bfill()
            elif method == 'knn':
                # KNN插值（简化版，使用最近的5个邻居）
                from sklearn.impute import KNNImputer
                imputer = KNNImputer(n_neighbors=5)
                # 只处理数值列
                numeric_cols = df_copy.select_dtypes(include=['float64', 'int64']).columns
                df_copy[numeric_cols] = imputer.fit_transform(df_copy[numeric_cols])
            
            return df_copy, missing_count
        except Exception as e:
            logger.error(f"处理{column}缺失值失败: {e}")
            return df, 0
    
    def normalize_minmax(self, df, columns):
        """Min-Max标准化"""
        try:
            df_copy = df.copy()
            for column in columns:
                if column in df_copy.columns:
                    min_val = df_copy[column].min()
                    max_val = df_copy[column].max()
                    if max_val > min_val:
                        df_copy[f'{column}_normalized'] = (df_copy[column] - min_val) / (max_val - min_val)
            return df_copy
        except Exception as e:
            logger.error(f"Min-Max标准化失败: {e}")
            return df
    
    def normalize_zscore(self, df, columns):
        """Z-score标准化"""
        try:
            df_copy = df.copy()
            for column in columns:
                if column in df_copy.columns:
                    mean_val = df_copy[column].mean()
                    std_val = df_copy[column].std()
                    if std_val > 0:
                        df_copy[f'{column}_zscore'] = (df_copy[column] - mean_val) / std_val
            return df_copy
        except Exception as e:
            logger.error(f"Z-score标准化失败: {e}")
            return df
    
    def encode_categorical(self, df):
        """编码分类变量"""
        try:
            df_copy = df.copy()
            
            # 城市编码
            city_mapping = {
                'beijing': 1,
                'shanghai': 2,
                'guangzhou': 3,
                'shenzhen': 4,
                'chengdu': 5
            }
            
            # 数据源编码
            source_mapping = {
                'OpenWeatherMap': 1,
                'Meteostat': 2,
                'Kaggle': 3
            }
            
            if 'city' in df_copy.columns:
                df_copy['city_id'] = df_copy['city'].map(city_mapping)
            
            if 'source' in df_copy.columns:
                df_copy['source_id'] = df_copy['source'].map(source_mapping)
            
            return df_copy
        except Exception as e:
            logger.error(f"编码分类变量失败: {e}")
            return df
    
    def process_time(self, df, time_column='timestamp'):
        """处理时间数据"""
        try:
            df_copy = df.copy()
            
            if time_column in df_copy.columns:
                # 转换为datetime类型
                df_copy[time_column] = pd.to_datetime(df_copy[time_column])
                
                # 提取时间维度
                df_copy['year'] = df_copy[time_column].dt.year
                df_copy['month'] = df_copy[time_column].dt.month
                df_copy['day'] = df_copy[time_column].dt.day
                df_copy['hour'] = df_copy[time_column].dt.hour
                df_copy['minute'] = df_copy[time_column].dt.minute
                df_copy['second'] = df_copy[time_column].dt.second
            
            return df_copy
        except Exception as e:
            logger.error(f"处理时间数据失败: {e}")
            return df
    
    def generate_cleaning_report(self, output_path='./logs'):
        """生成数据清洗报告"""
        try:
            # 确保输出目录存在
            os.makedirs(output_path, exist_ok=True)
            
            if not self.cleaning_logs:
                logger.warning("没有清洗日志记录")
                return False
            
            # 转换日志为DataFrame
            logs_df = pd.DataFrame(self.cleaning_logs)
            
            # 保存为CSV文件
            report_path = os.path.join(output_path, f'data_cleaning_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
            logs_df.to_csv(report_path, index=False, encoding='utf-8')
            
            # 生成汇总报告
            summary = logs_df.groupby(['process_type', 'field_name']).agg({
                'affected_count': 'sum',
                'process_method': 'first'
            }).reset_index()
            
            summary_path = os.path.join(output_path, f'data_cleaning_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
            summary.to_csv(summary_path, index=False, encoding='utf-8')
            
            logger.info(f"数据清洗报告已生成，保存到: {report_path}")
            logger.info(f"数据清洗汇总报告已生成，保存到: {summary_path}")
            
            return True
        except Exception as e:
            logger.error(f"生成数据清洗报告失败: {e}")
            return False
    
    def preprocess_data(self, df, data_type='historical'):
        """完整的数据预处理流程"""
        try:
            logger.info(f"开始数据预处理，数据类型: {data_type}")
            
            # 1. 处理时间数据
            df = self.process_time(df)
            
            # 2. 处理缺失值
            numeric_columns = ['temperature', 'pressure', 'humidity', 'precipitation', 'wind_speed', 'wind_direction']
            
            for column in numeric_columns:
                if column in df.columns:
                    if data_type == 'realtime':
                        # 实时数据使用前向填充
                        df, _ = self.handle_missing_values(df, column, method='ffill')
                    elif data_type == 'historical':
                        # 历史数据使用线性插值
                        df, _ = self.handle_missing_values(df, column, method='interpolate')
                    elif data_type == 'extreme':
                        # 极端事件数据使用均值填充
                        df, _ = self.handle_missing_values(df, column, method='mean')
            
            # 3. 处理异常值
            for column in numeric_columns:
                if column in df.columns:
                    df, _ = self.handle_outliers(df, column, method='interpolate')
            
            # 4. 编码分类变量
            df = self.encode_categorical(df)
            
            # 5. 数据标准化
            df = self.normalize_minmax(df, numeric_columns)
            df = self.normalize_zscore(df, numeric_columns)
            
            # 6. 确保没有NaN值（MySQL不支持NaN）
            for field in numeric_columns:
                if field in df.columns:
                    # 将NaN替换为0或其他合适的默认值
                    df[field] = df[field].fillna(0)
                    
            # 确保归一化后的列也没有NaN值
            for field in numeric_columns:
                normalized_cols = [f'{field}_normalized', f'{field}_zscore']
                for col in normalized_cols:
                    if col in df.columns:
                        df[col] = df[col].fillna(0)
            
            # 7. 生成清洗报告
            self.generate_cleaning_report()
            
            logger.info("数据预处理完成")
            return df
        except Exception as e:
            logger.error(f"数据预处理失败: {e}")
            return None

if __name__ == "__main__":
    # 示例用法
    import pandas as pd
    from datetime import datetime, timedelta
    
    # 创建示例数据
    dates = [datetime.now() - timedelta(hours=i) for i in range(100)]
    data = {
        'timestamp': dates,
        'city': ['beijing'] * 100,
        'temperature': [20 + np.random.normal(0, 5) for _ in range(100)],
        'pressure': [1013 + np.random.normal(0, 10) for _ in range(100)],
        'humidity': [60 + np.random.normal(0, 20) for _ in range(100)],
        'precipitation': [np.random.normal(0, 5) for _ in range(100)],
        'wind_speed': [5 + np.random.normal(0, 3) for _ in range(100)],
        'wind_direction': [np.random.uniform(0, 360) for _ in range(100)],
        'source': ['Meteostat'] * 100
    }
    
    # 添加一些异常值
    data['temperature'][10] = 100  # 异常高温
    data['temperature'][20] = -30  # 异常低温
    data['pressure'][30] = 1500     # 异常高压
    data['humidity'][40] = 150      # 异常高湿度
    data['precipitation'][50] = 1000  # 异常高降水量
    
    # 添加一些缺失值
    data['temperature'][60] = np.nan
    data['pressure'][70] = np.nan
    data['humidity'][80] = np.nan
    
    df = pd.DataFrame(data)
    
    # 创建预处理实例
    preprocessor = WeatherDataPreprocessor()
    
    # 执行预处理
    processed_df = preprocessor.preprocess_data(df, data_type='historical')
    
    if processed_df is not None:
        logger.info("示例数据预处理完成")
        print(processed_df.head())
        print("预处理前后数据形状:", df.shape, "->", processed_df.shape)
    else:
        logger.error("示例数据预处理失败")
