from flask import Flask, request, jsonify
import pandas as pd
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 数据存储路径
# 获取脚本所在目录的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, '../data')
PROCESSED_DATA_PATH = os.path.join(SCRIPT_DIR, '../data/processed')

class WeatherDataAPI:
    def __init__(self):
        self.data_files = self._get_data_files()
    
    def _get_data_files(self):
        """获取所有数据文件"""
        data_files = {
            'realtime': [],
            'historical': [],
            'processed': []
        }
        
        # 获取实时数据文件
        if os.path.exists(DATA_PATH):
            for filename in os.listdir(DATA_PATH):
                if filename.startswith('realtime') and filename.endswith('.json'):
                    data_files['realtime'].append(os.path.join(DATA_PATH, filename))
                elif filename.startswith('historical') and filename.endswith('.csv'):
                    data_files['historical'].append(os.path.join(DATA_PATH, filename))
        
        # 获取处理后的数据文件
        if os.path.exists(PROCESSED_DATA_PATH):
            for filename in os.listdir(PROCESSED_DATA_PATH):
                if filename.endswith('.csv'):
                    data_files['processed'].append(os.path.join(PROCESSED_DATA_PATH, filename))
        
        logger.info(f"发现数据文件: {data_files}")
        return data_files
    
    def _load_data(self, data_type='historical'):
        """加载指定类型的数据"""
        try:
            files = self.data_files[data_type]
            if not files:
                logger.warning(f"没有找到{data_type}类型的数据文件")
                return pd.DataFrame()
            
            # 加载所有文件并合并
            dfs = []
            for file in files:
                if file.endswith('.json'):
                    df = pd.read_json(file)
                else:
                    df = pd.read_csv(file)
                dfs.append(df)
            
            if not dfs:
                return pd.DataFrame()
            
            # 合并数据
            combined_df = pd.concat(dfs, ignore_index=True)
            
            # 转换时间格式
            if 'timestamp' in combined_df.columns:
                combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
            
            logger.info(f"成功加载{data_type}类型数据，共{len(combined_df)}条记录")
            return combined_df
            
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return pd.DataFrame()
    
    def query_data(self, params):
        """根据查询条件过滤数据"""
        try:
            # 加载所有数据
            all_data = []
            
            # 根据数据类型加载
            data_types = params.get('data_type', ['historical'])
            for data_type in data_types:
                df = self._load_data(data_type)
                if not df.empty:
                    all_data.append(df)
            
            if not all_data:
                return pd.DataFrame()
            
            # 合并所有数据
            df = pd.concat(all_data, ignore_index=True)
            
            # 1. 按城市过滤
            if 'city' in params:
                cities = params['city'] if isinstance(params['city'], list) else [params['city']]
                df = df[df['city'].isin(cities)]
            
            # 2. 按时间范围过滤
            if 'start_time' in params:
                start_time = pd.to_datetime(params['start_time'])
                df = df[df['timestamp'] >= start_time]
            
            if 'end_time' in params:
                end_time = pd.to_datetime(params['end_time'])
                df = df[df['timestamp'] <= end_time]
            
            # 3. 按指标过滤（选择列）
            if 'metrics' in params:
                metrics = params['metrics'] if isinstance(params['metrics'], list) else [params['metrics']]
                # 确保包含基本字段
                required_fields = ['timestamp', 'city', 'source']
                selected_fields = required_fields + [m for m in metrics if m not in required_fields]
                # 过滤掉不存在的字段
                selected_fields = [field for field in selected_fields if field in df.columns]
                df = df[selected_fields]
            
            # 4. 按数据源过滤
            if 'source' in params:
                sources = params['source'] if isinstance(params['source'], list) else [params['source']]
                df = df[df['source'].isin(sources)]
            
            # 5. 按数据质量过滤（如果有该字段）
            if 'quality' in params and 'quality' in df.columns:
                df = df[df['quality'] >= params['quality']]
            
            logger.info(f"查询完成，返回{len(df)}条记录")
            return df
            
        except Exception as e:
            logger.error(f"查询数据失败: {e}")
            return pd.DataFrame()
    
    def get_data_summary(self):
        """获取数据摘要信息"""
        try:
            # 加载所有数据
            all_data = []
            for data_type in ['realtime', 'historical', 'processed']:
                df = self._load_data(data_type)
                if not df.empty:
                    all_data.append(df)
            
            if not all_data:
                return {
                    'total_records': 0,
                    'cities': [],
                    'time_range': {'start': None, 'end': None},
                    'available_metrics': [],
                    'data_sources': []
                }
            
            df = pd.concat(all_data, ignore_index=True)
            
            # 生成摘要
            summary = {
                'total_records': len(df),
                'cities': sorted(df['city'].unique().tolist()),
                'time_range': {
                    'start': df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S') if not df['timestamp'].isnull().all() else None,
                    'end': df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S') if not df['timestamp'].isnull().all() else None
                },
                'available_metrics': [col for col in df.columns if col not in ['timestamp', 'city', 'source']],
                'data_sources': sorted(df['source'].unique().tolist()),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"生成数据摘要: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"生成数据摘要失败: {e}")
            return {}

# 初始化API
weather_api = WeatherDataAPI()

@app.route('/')
def home():
    return jsonify({
        'message': '气象数据查询API',
        'endpoints': {
            '/api/data': '查询气象数据',
            '/api/summary': '获取数据摘要',
            '/api/metrics': '获取可用指标'
        }
    })

@app.route('/api/data', methods=['GET'])
def get_data():
    """查询气象数据"""
    try:
        # 获取查询参数
        params = request.args.to_dict()
        
        # 处理列表参数
        if 'data_type' in params:
            params['data_type'] = params['data_type'].split(',')
        if 'city' in params:
            params['city'] = params['city'].split(',')
        if 'metrics' in params:
            params['metrics'] = params['metrics'].split(',')
        if 'source' in params:
            params['source'] = params['source'].split(',')
        
        logger.info(f"接收到查询请求: {params}")
        
        # 查询数据
        result_df = weather_api.query_data(params)
        
        if result_df.empty:
            return jsonify({
                'success': True,
                'message': '未找到匹配的数据',
                'data': [],
                'total_records': 0
            })
        
        # 转换为JSON格式
        result_df['timestamp'] = result_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        result = result_df.to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': result,
            'total_records': len(result)
        })
        
    except Exception as e:
        logger.error(f"API查询失败: {e}")
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}',
            'data': [],
            'total_records': 0
        }), 500

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """获取数据摘要"""
    try:
        summary = weather_api.get_data_summary()
        return jsonify({
            'success': True,
            'message': '获取数据摘要成功',
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"获取数据摘要失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取数据摘要失败: {str(e)}'
        }), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """获取可用指标"""
    try:
        summary = weather_api.get_data_summary()
        return jsonify({
            'success': True,
            'message': '获取可用指标成功',
            'data': {
                'available_metrics': summary['available_metrics'],
                'cities': summary['cities'],
                'data_sources': summary['data_sources']
            }
        })
        
    except Exception as e:
        logger.error(f"获取可用指标失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取可用指标失败: {str(e)}'
        }), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """刷新数据文件列表"""
    try:
        weather_api.data_files = weather_api._get_data_files()
        return jsonify({
            'success': True,
            'message': '数据文件列表已刷新',
            'data': weather_api.data_files
        })
        
    except Exception as e:
        logger.error(f"刷新数据文件列表失败: {e}")
        return jsonify({
            'success': False,
            'message': f'刷新数据文件列表失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)