# 气象数据字典

## 数据集描述
气象数据包含实时和历史的气温、气压、湿度、降水量、风速、风向等核心指标

## 数据来源
- OpenWeatherMap
- Meteostat
- Kaggle极端天气数据集

## 字段信息
| 字段名 | 描述 | 数据类型 | 单位 | 取值范围 | 格式 |
| --- | --- | --- | --- | --- | --- |
| timestamp | 数据采集时间 | datetime64[ns] | - | - | YYYY-MM-DD HH:MM:SS |
| city | 城市名称 | string | - | ['beijing', 'shanghai', 'guangzhou', 'shenzhen', 'chengdu'] | - |
| temperature | 气温 | float64 | °C | [-50, 60] | - |
| pressure | 气压 | float64 | hPa | [800, 1200] | - |
| humidity | 湿度 | float64 | % | [0, 100] | - |
| precipitation | 降水量 | float64 | mm | [0, 500] | - |
| wind_speed | 风速 | float64 | m/s | [0, 100] | - |
| wind_direction | 风向 | float64 | ° | [0, 360] | - |
| source | 数据来源 | string | - | ['OpenWeatherMap', 'Meteostat', 'Kaggle'] | - |

## 更新频率
实时数据每小时更新一次，历史数据按需获取

## 数据质量
经过格式验证、范围验证和标准化处理
