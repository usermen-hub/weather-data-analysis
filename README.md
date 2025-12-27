# 气象数据分析系统 - 数据采集与处理模块

## 项目简介

本项目是气象数据分析大作业的第一部分，负责多源数据采集、合规校验与初加工。主要功能包括：

1. **数据采集**：获取气温、气压、湿度、降水量、风速、风向6大核心指标的实时及历史数据
2. **极端天气数据**：下载Kaggle极端天气数据集，补充极端气象事件样本
3. **数据合规与标准化**：开展数据合规性校验，统一数据格式与单位
4. **数据字典生成**：编制详细数据字典，明确字段含义、数据类型及取值范围
5. **数据查询接口**：开发简易数据查询API，支持团队成员按指标、时间、区域等条件查询数据

## 项目结构

```
weather_data/
├── data_sources/          # 数据采集模块
│   └── data_collector.py  # 气象数据采集脚本
├── processing/            # 数据处理模块
│   ├── data_validator.py      # 数据验证与标准化脚本
│   ├── data_preprocessor.py   # 数据预处理脚本
│   ├── database_manager.py    # 数据库管理脚本
│   └── data_storage.py        # 数据存储脚本
├── api/                   # API接口模块
│   └── app.py             # Flask API应用
├── data/                  # 数据存储目录（自动生成）
│   └── processed/         # 处理后的数据目录（自动生成）
├── docs/                  # 文档目录
│   ├── data_dictionary.json  # 数据字典（JSON格式）
│   └── data_dictionary.md    # 数据字典（Markdown格式）
├── .env                   # 环境变量配置
├── requirements.txt       # 依赖库列表
├── main.py                # 主脚本
├── load_and_store_csv.py  # CSV数据加载与存储脚本
├── view_database.py       # 数据库查看工具
└── README.md              # 项目说明文档
```

## 环境要求

- Python 3.7+
- pip 20.0+

## 安装与配置

### 1. 安装依赖库

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件，填写所需的API密钥和数据库连接信息：

```
# OpenWeatherMap API Key
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Kaggle API Credentials
KAGGLE_USERNAME=your_kaggle_username_here
KAGGLE_KEY=your_kaggle_key_here

# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=weather_data
DB_USER=root
DB_PASSWORD=your_mysql_password_here
```

- **OpenWeatherMap API Key**：注册 [OpenWeatherMap](https://openweathermap.org/) 账号获取
- **Kaggle API Credentials**：登录 [Kaggle](https://www.kaggle.com/) 账号，在个人设置中创建API密钥
- **MySQL Database Configuration**：填写您的MySQL数据库连接信息，包括主机、端口、数据库名、用户名和密码

## 使用方法

### 1. 运行主脚本

```bash
python main.py
```

主脚本将执行以下操作：
- 生成数据字典
- 获取5个城市（北京、上海、广州、深圳、成都）的实时气象数据
- 获取上述城市最近30天的历史气象数据
- 下载Kaggle极端天气数据集
- 处理并标准化所有数据

### 2. 加载和存储CSV数据

```bash
python load_and_store_csv.py
```

该脚本将：
- 读取 `data/` 目录下的所有CSV文件
- 根据文件名判断数据类型（实时、历史、极端）
- 预处理数据（处理缺失值、异常值、归一化等）
- 将数据存入MySQL数据库
- 支持新增和更新数据

### 3. 查看数据库数据

```bash
python view_database.py
```

交互式数据库查看工具，支持：
- 查看所有表的数据行数统计
- 查看指定表的详细数据
- 查看特定城市的历史天气数据

使用说明：
1. 运行脚本后，根据提示选择操作
2. 选项 1：查看所有表的数据行数
3. 选项 2：查看指定表的数据（如 cities、data_sources、historical_weather 等）
4. 选项 3：查看特定城市的历史天气数据
5. 选项 4：退出程序

### 4. 启动数据查询API

```bash
python api/app.py
```

API将在 `http://localhost:5000` 启动，提供以下端点：

- `GET /`：API首页，显示可用端点
- `GET /api/data`：查询气象数据，支持多种过滤条件
- `GET /api/summary`：获取数据摘要信息
- `GET /api/metrics`：获取可用指标列表
- `POST /api/refresh`：刷新数据文件列表

### 5. API查询示例

#### 查询北京的实时气温和湿度

```
http://localhost:5000/api/data?city=beijing&metrics=temperature,humidity&data_type=realtime
```

#### 查询上海最近7天的降水量数据

```
http://localhost:5000/api/data?city=shanghai&metrics=precipitation&start_time=2023-05-01&end_time=2023-05-07
```

#### 查询所有城市的风速和风向数据

```
http://localhost:5000/api/data?metrics=wind_speed,wind_direction
```

## 数据格式

### 核心指标

| 指标名称 | 字段名 | 单位 | 数据类型 |
|---------|--------|------|----------|
| 气温 | temperature | °C | float64 |
| 气压 | pressure | hPa | float64 |
| 湿度 | humidity | % | float64 |
| 降水量 | precipitation | mm | float64 |
| 风速 | wind_speed | m/s | float64 |
| 风向 | wind_direction | ° | float64 |

### 数据来源

- **OpenWeatherMap**：提供实时气象数据
- **Meteostat**：提供历史气象数据
- **Kaggle**：提供极端天气事件数据

## 数据字典

数据字典将自动生成在 `docs/` 目录下，包括：
- `data_dictionary.json`：JSON格式，便于程序读取
- `data_dictionary.md`：Markdown格式，便于人工阅读

## 数据库表结构

### 1. 城市表 (cities)

| 字段名 | 数据类型 | 含义 | 说明 |
|-------|---------|------|------|
| city_id | Integer | 城市ID | 主键，自增长 |
| city_name | String | 城市名称 | 英文名称，如 'beijing' |
| city_code | String | 城市编码 | 如 'BJ' |
| latitude | DECIMAL(10,6) | 纬度 | 城市地理纬度 |
| longitude | DECIMAL(10,6) | 经度 | 城市地理经度 |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动生成，更新时自动更新 |

### 2. 数据源表 (data_sources)

| 字段名 | 数据类型 | 含义 | 说明 |
|-------|---------|------|------|
| source_id | Integer | 数据源ID | 主键，自增长 |
| source_name | String | 数据源名称 | 如 'OpenWeatherMap' |
| source_code | String | 数据源编码 | 如 'OWM' |
| description | Text | 数据源描述 | 详细说明数据源信息 |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动生成，更新时自动更新 |

### 3. 历史天气表 (historical_weather)

| 字段名 | 数据类型 | 含义 | 说明 |
|-------|---------|------|------|
| id | BigInteger | 记录ID | 主键，自增长 |
| city_id | Integer | 城市ID | 外键，关联cities表 |
| source_id | Integer | 数据源ID | 外键，关联data_sources表 |
| timestamp | DateTime | 数据采集时间 | 精确到小时 |
| temperature | DECIMAL(5,2) | 气温 | °C |
| pressure | DECIMAL(6,2) | 气压 | hPa |
| humidity | DECIMAL(5,2) | 湿度 | % |
| precipitation | DECIMAL(6,2) | 降水量 | mm |
| wind_speed | DECIMAL(5,2) | 风速 | m/s |
| wind_direction | DECIMAL(5,2) | 风向 | ° |
| status | SmallInteger | 数据状态 | 0:无效, 1:有效 |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动生成，更新时自动更新 |

### 4. 实时天气表 (real_time_weather)

| 字段名 | 数据类型 | 含义 | 说明 |
|-------|---------|------|------|
| id | BigInteger | 记录ID | 主键，自增长 |
| city_id | Integer | 城市ID | 外键，关联cities表 |
| source_id | Integer | 数据源ID | 外键，关联data_sources表 |
| timestamp | DateTime | 数据采集时间 | 精确到分钟 |
| temperature | DECIMAL(5,2) | 气温 | °C |
| pressure | DECIMAL(6,2) | 气压 | hPa |
| humidity | DECIMAL(5,2) | 湿度 | % |
| precipitation | DECIMAL(6,2) | 降水量 | mm |
| wind_speed | DECIMAL(5,2) | 风速 | m/s |
| wind_direction | DECIMAL(5,2) | 风向 | ° |
| status | SmallInteger | 数据状态 | 0:无效, 1:有效 |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动生成，更新时自动更新 |

### 5. 极端事件表 (extreme_events)

| 字段名 | 数据类型 | 含义 | 说明 |
|-------|---------|------|------|
| event_id | BigInteger | 事件ID | 主键，自增长 |
| city_id | Integer | 城市ID | 外键，关联cities表 |
| source_id | Integer | 数据源ID | 外键，关联data_sources表 |
| event_type | String | 事件类型 | 如 '暴雨', '高温' |
| event_level | SmallInteger | 事件等级 | 1-5级 |
| start_time | DateTime | 事件开始时间 | |
| end_time | DateTime | 事件结束时间 | |
| max_temperature | DECIMAL(5,2) | 最大气温 | °C |
| min_temperature | DECIMAL(5,2) | 最小气温 | °C |
| max_pressure | DECIMAL(6,2) | 最大气压 | hPa |
| min_pressure | DECIMAL(6,2) | 最小气压 | hPa |
| max_humidity | DECIMAL(5,2) | 最大湿度 | % |
| max_precipitation | DECIMAL(6,2) | 最大降水量 | mm |
| max_wind_speed | DECIMAL(5,2) | 最大风速 | m/s |
| description | Text | 事件描述 | 详细说明 |
| status | SmallInteger | 数据状态 | 0:无效, 1:有效 |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动生成，更新时自动更新 |

### 6. 数据清洗日志表 (data_cleaning_logs)

| 字段名 | 数据类型 | 含义 | 说明 |
|-------|---------|------|------|
| log_id | BigInteger | 日志ID | 主键，自增长 |
| process_time | DateTime | 处理时间 | 数据处理时间 | |
| data_source | String | 数据源 | 数据源名称 |
| field_name | String | 字段名 | 如 'temperature' |
| process_type | String | 处理类型 | 如 '异常值检测', '缺失值处理' |
| process_method | String | 处理方法 | 如 'interpolate' |
| before_count | Integer | 处理前数量 |
| after_count | Integer | 处理后数量 |
| affected_count | Integer | 受影响数量 |
| description | Text | 处理描述 |
| created_at | DateTime | 创建时间 | 自动生成 |

## 协作说明

1. 本模块生成的标准化数据文件将存储在 `data/` 目录下
2. 清洗和处理后的数据将存入MySQL数据库
3. 团队成员可通过以下方式获取数据：
   - 使用 `view_database.py` 查看数据库数据
   - 通过API接口查询所需数据
4. 数据字典详细说明了所有字段的含义和格式
5. 如有新的数据源或指标需要添加，可修改以下文件：
   - `data_collector.py`：数据采集逻辑
   - `data_validator.py`：数据验证与标准化
   - `data_preprocessor.py`：数据预处理逻辑
   - `database_manager.py`：数据库表结构

## 注意事项

1. 首次运行需要确保网络连接正常
2. Kaggle数据集下载可能需要较长时间，取决于网络速度
3. API接口默认使用5000端口，如需修改请编辑 `.env` 文件
4. 建议定期运行 `main.py` 更新数据
5. 确保MySQL数据库已安装并运行，且配置信息正确
6. 首次运行时会自动创建数据库和表结构
7. 数据预处理会自动处理缺失值、异常值和归一化
8. 数据库连接信息存储在 `.env` 文件中，请妥善保管
9. 建议定期备份数据库，防止数据丢失

## 数据预处理流程

1. **缺失值处理**：
   - 实时数据：前向填充
   - 历史数据：线性插值
   - 极端事件数据：均值填充

2. **异常值检测与处理**：
   - 使用IQR方法检测异常值
   - 使用业务规则检测异常值
   - 异常值处理方法：线性插值

3. **数据归一化**：
   - Min-Max归一化：将数据缩放到[0, 1]区间
   - Z-score归一化：将数据转换为均值为0，标准差为1的分布

4. **数据编码**：
   - 城市编码：将城市名称转换为数字ID
   - 数据源编码：将数据源名称转换为数字ID

5. **数据格式转换**：
   - 时间格式转换：确保时间格式统一
   - 数值类型转换：确保数据类型正确
   - 单位统一：确保所有数据单位一致

6. **NaN值处理**：
   - 将所有NaN值替换为0，确保MySQL兼容性

## 更新日志

- v2.0.0：添加数据预处理和数据库功能
  - 新增数据预处理模块，支持缺失值、异常值处理和归一化
  - 新增MySQL数据库存储功能
  - 新增数据查看工具
  - 完善数据处理流程
  - 修复了数据存储中的NaN值问题
- v1.0.0：初始版本，实现核心功能
