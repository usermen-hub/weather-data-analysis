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
│   └── data_validator.py  # 数据验证与标准化脚本
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

编辑 `.env` 文件，填写所需的API密钥：

```
# OpenWeatherMap API Key
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Kaggle API Credentials
KAGGLE_USERNAME=your_kaggle_username_here
KAGGLE_KEY=your_kaggle_key_here
```

- **OpenWeatherMap API Key**：注册 [OpenWeatherMap](https://openweathermap.org/) 账号获取
- **Kaggle API Credentials**：登录 [Kaggle](https://www.kaggle.com/) 账号，在个人设置中创建API密钥

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

### 2. 启动数据查询API

```bash
python api/app.py
```

API将在 `http://localhost:5000` 启动，提供以下端点：

- `GET /`：API首页，显示可用端点
- `GET /api/data`：查询气象数据，支持多种过滤条件
- `GET /api/summary`：获取数据摘要信息
- `GET /api/metrics`：获取可用指标列表
- `POST /api/refresh`：刷新数据文件列表

### 3. API查询示例

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

## 协作说明

1. 本模块生成的标准化数据文件将存储在 `data/` 目录下
2. 团队成员可通过API接口查询所需数据
3. 数据字典详细说明了所有字段的含义和格式
4. 如有新的数据源或指标需要添加，可修改 `data_collector.py` 和 `data_validator.py`

## 注意事项

1. 首次运行需要确保网络连接正常
2. Kaggle数据集下载可能需要较长时间，取决于网络速度
3. API接口默认使用5000端口，如需修改请编辑 `.env` 文件
4. 建议定期运行 `main.py` 更新数据



## 更新日志

- v1.0.0：初始版本，实现核心功能
