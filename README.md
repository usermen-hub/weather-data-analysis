# 气象数据分析与可视化系统

## 项目简介

本项目是一个完整的气象数据分析与可视化系统，包含四个主要部分：

### （一）数据采集模块
1. **数据采集**：获取气温、气压、湿度、降水量、风速、风向6大核心指标的实时及历史数据
2. **极端天气数据**：下载Kaggle极端天气数据集，补充极端气象事件样本

### （二）数据处理模块
3. **数据合规与标准化**：开展数据合规性校验，统一数据格式与单位
4. **数据字典生成**：编制详细数据字典，明确字段含义、数据类型及取值范围
5. **数据查询接口**：开发简易数据查询API，支持团队成员按指标、时间、区域等条件查询数据

### （三）数据分析与建模模块
6. **多维度数据分析**：开展时间维度分析（日/月/季气象指标变化趋势）、区域维度分析（不同城市/区域气象指标对比）、关联维度分析（各气象指标间相关性）
7. **极端事件识别**：建立暴雨、高温、寒潮等极端气象事件识别规则，基于预处理后的数据精准识别极端事件
8. **短期气象预测**：基于ARIMA模型构建预测模型，实现未来3天气温、降水量的精准预测

### （四）可视化与系统集成模块
9. **可视化图表开发**：设计折线图、柱状图、热力图、雷达图等多类型可视化图表
10. **交互式功能搭建**：搭建一体化交互式仪表盘，支持多维度查询与筛选
11. **系统集成与优化**：整合全模块功能，集成极端天气智能预警模块；优化UI界面布局与交互逻辑
12. **图表导出功能**：支持可视化图表导出为图片、Excel等格式

## 项目结构

```
weather_data/
├── analysis/              # 数据分析与建模模块
│   └── data_analyzer.py   # 气象数据分析与预测脚本
├── data_sources/          # 数据采集模块
│   └── data_collector.py  # 气象数据采集脚本
├── processing/            # 数据处理模块
│   ├── data_validator.py      # 数据验证与标准化脚本
│   ├── data_preprocessor.py   # 数据预处理脚本
│   ├── database_manager.py    # 数据库管理脚本
│   └── data_storage.py        # 数据存储脚本
├── api/                   # API接口模块
│   └── app.py             # Flask API应用
├── visualization/         # 可视化与仪表盘模块
│   ├── charts.py          # 图表生成脚本
│   └── dashboard.py       # Dash交互式仪表盘应用
├── data/                  # 数据存储目录（自动生成）
│   └── processed/         # 处理后的数据目录（自动生成）
├── docs/                  # 文档目录
│   ├── data_dictionary.json  # 数据字典（JSON格式）
│   └── data_dictionary.md    # 数据字典（Markdown格式）
├── logs/                  # 日志目录（自动生成）
├── .env                   # 环境变量配置
├── requirements.txt       # 依赖库列表
├── main.py                # 主脚本
├── load_and_store_csv.py  # CSV数据加载与存储脚本
├── view_database.py       # 数据库查看工具
├── test_system.py         # 系统测试脚本
├── test_analysis.py       # 数据分析功能测试脚本
└── README.md              # 项目说明文档
```

## 环境要求

- Python 3.9+
- pip 22.0+

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

### 5. 数据分析功能测试

```bash
python test_analysis.py
```

测试数据分析和预测功能，包括：
- 获取历史数据
- 时间维度分析（日/月/季节）
- 区域维度分析
- 关联维度分析
- 极端事件识别
- ARIMA短期预测
- 智能预警功能

### 6. 启动交互式可视化仪表盘

```bash
python visualization/dashboard.py
```

Dash交互式仪表盘将在 `http://localhost:8050` 启动，提供以下功能：

- **多维度数据分析**：支持时间/区域/关联维度分析，可选择不同图表类型
- **极端事件识别**：可视化展示极端天气事件分布和时间线
- **短期气象预测**：基于ARIMA模型的未来3天气象预测
- **智能预警系统**：支持自定义预警阈值，实时检测预警条件

### 7. 运行系统测试

```bash
python test_system.py
```

系统全面测试，包括：
- 数据预处理功能测试
- 数据库初始化功能测试
- 数据存储功能测试

## 数据分析与建模功能

### 1. 多维度数据分析

#### 时间维度分析
- 支持日/月/季节气象指标变化趋势分析
- 计算均值、最大值、最小值、标准差等统计指标
- 自动生成季节映射（春/夏/秋/冬）

#### 区域维度分析
- 支持多城市气象指标对比
- 支持按日/月时间周期分析
- 生成城市间气象指标对比图表

#### 关联维度分析
- 计算各气象指标间的相关性矩阵
- 支持热力图可视化展示
- 识别指标间的强相关关系

### 2. 极端事件识别

- 建立了暴雨、高温、寒潮、大风、高湿、干燥等极端事件识别规则
- 支持自定义事件阈值
- 记录事件发生时间、区域及核心指标数据
- 支持可视化展示事件分布和时间线

### 3. 短期气象预测

- 基于ARIMA模型实现未来3天气温、降水量预测
- 自动处理数据频率和缺失值
- 生成包含预测结果和95%置信区间的分析报告
- 支持模型参数调优

## 可视化与仪表盘功能

### 1. 图表类型

- **折线图**：展示时间序列趋势
- **柱状图**：展示区域对比和分组数据
- **热力图**：展示指标相关性和时间-区域分布
- **雷达图**：展示多指标综合对比
- **散点图**：展示指标间关系
- **箱线图**：展示数据分布
- **直方图**：展示数据频率分布

### 2. 交互式功能

- **多维度筛选**：支持按城市、时间范围、指标类型筛选
- **动态图表切换**：支持在不同图表类型间切换
- **实时数据更新**：自动从数据库获取最新数据
- **图表导出**：支持将数据导出为CSV格式

### 3. 智能预警系统

- **自定义阈值**：支持设置不同指标的预警阈值
- **多条件支持**：支持大于、小于、等于等条件
- **实时检测**：检查最近24小时数据是否触发预警
- **历史记录**：展示最近30天的预警历史

## 系统集成与优化

### 1. 模块集成

- 整合了数据采集、预处理、分析、预测、可视化全流程
- 统一的数据接口设计
- 模块化架构，便于扩展和维护

### 2. 性能优化

- 数据缓存机制，提高查询效率
- 异步数据处理，减少等待时间
- 优化的数据库查询，降低响应时间

### 3. 安全性设计

- 环境变量管理敏感信息
- 输入参数验证，防止恶意输入
- 数据库连接池管理

### 4. 可扩展性

- 支持添加新的数据源
- 支持添加新的气象指标
- 支持自定义分析算法
- 支持新的可视化图表类型

## 数据导出功能

### 1. 数据导出

- 支持将图表数据导出为CSV格式
- 支持自定义文件名和导出范围
- 导出数据包含完整的指标信息和时间戳

### 2. 导出使用说明

1. 在仪表盘界面选择要导出的数据
2. 点击"导出图表"按钮
3. 系统自动生成CSV文件并下载
4. 导出的CSV文件包含当前筛选条件下的所有数据

## API查询示例

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

1. 本系统整合了数据采集、预处理、分析、预测、可视化全流程
2. 清洗和处理后的数据将存入MySQL数据库
3. 团队成员可通过以下方式获取数据：
   - 使用 `view_database.py` 查看数据库数据
   - 通过API接口查询所需数据
   - 使用交互式仪表盘进行可视化分析
4. 数据字典详细说明了所有字段的含义和格式
5. 如有新的数据源或指标需要添加，可修改以下文件：
   - `data_collector.py`：数据采集逻辑
   - `data_validator.py`：数据验证与标准化
   - `data_preprocessor.py`：数据预处理逻辑
   - `database_manager.py`：数据库表结构
   - `data_analyzer.py`：数据分析与预测逻辑
   - `charts.py`：图表生成逻辑
   - `dashboard.py`：仪表盘应用

## 注意事项

1. 首次运行需要确保网络连接正常
2. Kaggle数据集下载可能需要较长时间，取决于网络速度
3. API接口默认使用5000端口，仪表盘默认使用8050端口
4. 建议定期运行 `main.py` 更新数据
5. 确保MySQL数据库已安装并运行，且配置信息正确
6. 首次运行时会自动创建数据库和表结构
7. 数据预处理会自动处理缺失值、异常值和归一化
8. 数据库连接信息存储在 `.env` 文件中，请妥善保管
9. 建议定期备份数据库，防止数据丢失
10. 运行仪表盘需要安装dash、plotly和statsmodels库

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

- v4.0.0：添加数据分析与可视化功能
  - 新增数据分析模块，支持多维度分析（时间/区域/关联）
  - 实现极端事件识别功能
  - 基于ARIMA模型实现短期气象预测
  - 开发了基于Plotly的图表生成功能
  - 搭建了Dash交互式仪表盘
  - 集成了智能预警系统
  - 支持图表数据导出功能
- v3.0.0：添加系统测试和优化
  - 新增系统测试脚本
  - 完善了数据分析功能
  - 修复了ARIMA预测中的数据频率问题
  - 优化了数据查询性能
- v2.0.0：添加数据预处理和数据库功能
  - 新增数据预处理模块，支持缺失值、异常值处理和归一化
  - 新增MySQL数据库存储功能
  - 新增数据查看工具
  - 完善数据处理流程
  - 修复了数据存储中的NaN值问题
- v1.0.0：初始版本，实现核心功能
