# 数据预处理与存储方案

## 1. 数据清洗优化方案

### 1.1 异常值检测与处理

#### 检测方法
1. **IQR（四分位距）方法**：
   - 计算每个数值字段的四分位数Q1和Q3
   - 计算IQR = Q3 - Q1
   - 异常值定义为：小于Q1 - 1.5*IQR 或 大于Q3 + 1.5*IQR
   - 适用于：temperature, pressure, humidity, precipitation, wind_speed

2. **Z-score方法**：
   - 计算每个数值的Z-score = (x - μ) / σ
   - 异常值定义为：|Z-score| > 3
   - 适用于：wind_direction

3. **基于业务规则的检测**：
   - 温度：[-50°C, 60°C] 外为异常值
   - 气压：[800hPa, 1200hPa] 外为异常值
   - 湿度：[0%, 100%] 外为异常值
   - 降水量：[0mm, 500mm] 外为异常值
   - 风速：[0m/s, 100m/s] 外为异常值
   - 风向：[0°, 360°] 外为异常值

#### 处理策略
- 对检测到的异常值，先记录日志，然后：
  - 对于连续型数据：使用线性插值或均值填充
  - 对于离散型数据：使用众数填充
  - 对于极端异常值：标记为缺失值，后续统一处理

### 1.2 缺失值处理

#### 缺失值类型
1. **完全随机缺失（MCAR）**：缺失与任何变量无关
2. **随机缺失（MAR）**：缺失与其他变量有关
3. **非随机缺失（MNAR）**：缺失与变量本身有关

#### 处理方法
1. **均值/中位数/众数填充**：
   - 适用于数值型变量，填充后保持数据分布不变

2. **线性插值**：
   - 适用于时间序列数据，根据前后值进行线性插值
   - 优点：保留时间序列的趋势性

3. **KNN插值**：
   - 基于相似度的插值方法，考虑多个变量的关系
   - 适用于多变量数据

4. **前向填充（FFill）和后向填充（BFill）**：
   - 适用于时间序列数据，使用前一个或后一个有效观测值填充

#### 处理策略
- 对于实时数据：使用前向填充
- 对于历史数据：使用线性插值
- 对于极端天气数据：使用均值填充

### 1.3 数据清洗日志

#### 日志内容
1. **处理规则**：记录使用的异常值检测方法、缺失值处理方法
2. **处理数量**：记录每个字段的异常值数量、缺失值数量
3. **处理效果**：记录处理前后的数据分布变化、统计指标变化

#### 日志格式
- 时间戳
- 字段名
- 处理类型（异常值检测/缺失值处理）
- 处理方法
- 处理前数量
- 处理后数量
- 处理效果描述

## 2. 数据基础标准化方案

### 2.1 文本类型标签编码

#### 城市编码
| 城市名称 | 城市编码 |
|---------|---------|
| beijing | 1 |
| shanghai | 2 |
| guangzhou | 3 |
| shenzhen | 4 |
| chengdu | 5 |

#### 数据源编码
| 数据源名称 | 数据源编码 |
|-----------|-----------|
| OpenWeatherMap | 1 |
| Meteostat | 2 |
| Kaggle | 3 |

### 2.2 非结构化数据处理

#### 天气状况描述处理
- 将天气状况文本转换为结构化标签
- 例如："Clear sky" → "晴" → 1

#### 时间数据处理
- 统一时间格式：YYYY-MM-DD HH:MM:SS
- 提取年、月、日、时、分、秒等时间维度

### 2.3 数据标准化

#### 数值标准化
1. **Min-Max标准化**：
   - 公式：x' = (x - min) / (max - min)
   - 适用于：所有数值型变量

2. **Z-score标准化**：
   - 公式：x' = (x - μ) / σ
   - 适用于：需要保留原始分布特征的变量

## 3. MySQL数据库存储架构设计

### 3.1 数据库表结构

#### 3.1.1 城市表（cities）
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| city_id | INT | PRIMARY KEY AUTO_INCREMENT | 城市ID |
| city_name | VARCHAR(50) | UNIQUE NOT NULL | 城市名称 |
| city_code | VARCHAR(20) | NOT NULL | 城市编码 |
| latitude | DECIMAL(10,6) | NOT NULL | 纬度 |
| longitude | DECIMAL(10,6) | NOT NULL | 经度 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### 3.1.2 数据源表（data_sources）
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| source_id | INT | PRIMARY KEY AUTO_INCREMENT | 数据源ID |
| source_name | VARCHAR(100) | UNIQUE NOT NULL | 数据源名称 |
| source_code | VARCHAR(20) | NOT NULL | 数据源编码 |
| description | TEXT | | 数据源描述 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### 3.1.3 实时数据表（real_time_weather）
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | BIGINT | PRIMARY KEY AUTO_INCREMENT | 记录ID |
| city_id | INT | FOREIGN KEY REFERENCES cities(city_id) | 城市ID |
| source_id | INT | FOREIGN KEY REFERENCES data_sources(source_id) | 数据源ID |
| timestamp | DATETIME | NOT NULL | 数据采集时间 |
| temperature | DECIMAL(5,2) | | 气温（°C） |
| pressure | DECIMAL(6,2) | | 气压（hPa） |
| humidity | DECIMAL(5,2) | | 湿度（%） |
| precipitation | DECIMAL(6,2) | | 降水量（mm） |
| wind_speed | DECIMAL(5,2) | | 风速（m/s） |
| wind_direction | DECIMAL(5,2) | | 风向（°） |
| status | TINYINT | DEFAULT 1 | 数据状态（0:无效, 1:有效） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引**：
- INDEX idx_city_timestamp (city_id, timestamp DESC)

#### 3.1.4 历史数据表（historical_weather）
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| id | BIGINT | PRIMARY KEY AUTO_INCREMENT | 记录ID |
| city_id | INT | FOREIGN KEY REFERENCES cities(city_id) | 城市ID |
| source_id | INT | FOREIGN KEY REFERENCES data_sources(source_id) | 数据源ID |
| timestamp | DATETIME | NOT NULL | 数据采集时间 |
| temperature | DECIMAL(5,2) | | 气温（°C） |
| pressure | DECIMAL(6,2) | | 气压（hPa） |
| humidity | DECIMAL(5,2) | | 湿度（%） |
| precipitation | DECIMAL(6,2) | | 降水量（mm） |
| wind_speed | DECIMAL(5,2) | | 风速（m/s） |
| wind_direction | DECIMAL(5,2) | | 风向（°） |
| status | TINYINT | DEFAULT 1 | 数据状态（0:无效, 1:有效） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引**：
- INDEX idx_city_timestamp (city_id, timestamp)
- INDEX idx_timestamp (timestamp)

#### 3.1.5 极端事件数据表（extreme_events）
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| event_id | BIGINT | PRIMARY KEY AUTO_INCREMENT | 事件ID |
| city_id | INT | FOREIGN KEY REFERENCES cities(city_id) | 城市ID |
| source_id | INT | FOREIGN KEY REFERENCES data_sources(source_id) | 数据源ID |
| event_type | VARCHAR(50) | NOT NULL | 事件类型（暴雨、高温、大风等） |
| event_level | TINYINT | NOT NULL | 事件等级（1-5级） |
| start_time | DATETIME | NOT NULL | 事件开始时间 |
| end_time | DATETIME | NOT NULL | 事件结束时间 |
| max_temperature | DECIMAL(5,2) | | 最大气温（°C） |
| min_temperature | DECIMAL(5,2) | | 最小气温（°C） |
| max_pressure | DECIMAL(6,2) | | 最大气压（hPa） |
| min_pressure | DECIMAL(6,2) | | 最小气压（hPa） |
| max_humidity | DECIMAL(5,2) | | 最大湿度（%） |
| max_precipitation | DECIMAL(6,2) | | 最大降水量（mm） |
| max_wind_speed | DECIMAL(5,2) | | 最大风速（m/s） |
| description | TEXT | | 事件描述 |
| status | TINYINT | DEFAULT 1 | 数据状态（0:无效, 1:有效） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引**：
- INDEX idx_city_event (city_id, event_type, start_time)
- INDEX idx_event_time (start_time, end_time)

#### 3.1.6 数据清洗日志表（data_cleaning_logs）
| 字段名 | 数据类型 | 约束 | 描述 |
|-------|---------|------|------|
| log_id | BIGINT | PRIMARY KEY AUTO_INCREMENT | 日志ID |
| process_time | DATETIME | NOT NULL | 处理时间 |
| data_source | VARCHAR(100) | NOT NULL | 数据源 |
| field_name | VARCHAR(50) | NOT NULL | 字段名 |
| process_type | VARCHAR(50) | NOT NULL | 处理类型（异常值检测/缺失值处理） |
| process_method | VARCHAR(100) | NOT NULL | 处理方法 |
| before_count | INT | NOT NULL | 处理前数量 |
| after_count | INT | NOT NULL | 处理后数量 |
| affected_count | INT | NOT NULL | 受影响数量 |
| description | TEXT | | 处理描述 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 3.2 数据库设计原则

1. **范式化设计**：
   - 遵循第三范式（3NF），减少数据冗余
   - 分离城市、数据源等基础信息到独立表

2. **高性能设计**：
   - 为频繁查询的字段创建索引
   - 分区表设计（按时间分区）
   - 合理设置数据类型，减少存储空间

3. **可扩展性设计**：
   - 支持新增城市、数据源
   - 支持新增气象指标
   - 支持不同时间粒度的数据存储

## 4. 数据增量更新策略

### 4.1 实时数据更新
1. **采集频率**：每小时采集一次
2. **更新方式**：
   - 先查询实时数据表中是否已存在该时间点的数据
   - 若存在，更新数据；若不存在，插入新数据
   - 更新时保留历史版本，用于审计和回溯

### 4.2 历史数据更新
1. **更新频率**：每天更新一次
2. **更新方式**：
   - 批量插入新的历史数据
   - 对已存在的数据进行增量更新
   - 定期清理重复数据

### 4.3 极端事件数据更新
1. **更新频率**：实时检测，定期更新
2. **更新方式**：
   - 实时检测极端天气事件
   - 若检测到新事件，插入新记录
   - 对已存在的事件进行状态更新

## 5. 技术栈

- **数据处理**：Python 3.7+, pandas, numpy
- **数据库**：MySQL 8.0+
- **ORM框架**：SQLAlchemy
- **日志管理**：logging模块
- **配置管理**：python-dotenv

## 6. 实现步骤

1. **创建数据预处理模块**：
   - 实现异常值检测功能
   - 实现缺失值处理功能
   - 实现数据标准化功能
   - 实现数据清洗日志记录功能

2. **创建数据库连接模块**：
   - 实现数据库连接池
   - 实现数据库初始化功能
   - 实现数据迁移功能

3. **创建数据存储模块**：
   - 实现实时数据存储功能
   - 实现历史数据存储功能
   - 实现极端事件数据存储功能
   - 实现数据增量更新功能

4. **测试和验证**：
   - 测试数据预处理功能
   - 测试数据库连接和初始化功能
   - 测试数据存储和增量更新功能
   - 验证数据一致性和完整性

5. **集成到现有系统**：
   - 将数据预处理和存储模块集成到现有系统
   - 实现与API服务的对接
   - 提供数据查询接口
