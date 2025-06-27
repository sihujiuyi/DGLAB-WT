# 郊狼 3.0 控制程序

这是一个用于控制郊狼 3.0 设备的 Python 应用程序，提供了实时数据获取、处理和设备控制功能。

## 功能特性

- 实时数据获取和处理
- 自动强度调节
- 图形化配置界面
- 支持 Windows 和 Unix-like 系统
- 自动保存和加载配置
- 日志记录功能

## 系统要求

- Python >= 3.13
- 依赖包：
  - pydglab == 1.0.0
  - requests == 2.32.4

## 项目结构

```
.
├── c2dglab.py          # 主程序模块：设备控制和强度调节
├── data_fetcher.py     # 数据获取模块：从游戏获取实时数据
├── config.pyw          # 配置界面：参数调整
├── global_vars.py      # 全局变量管理
├── config.json         # 配置文件
├── 点我启动.bat         # Windows 启动脚本
└── run.sh             # Unix 启动脚本
```

## 详细逻辑说明

### 数据获取逻辑 (data_fetcher.py)

1. **数据源**
   - 从 `http://localhost:8111/indicators` 获取游戏的陆战载具数据
   - 从 `http://localhost:8111/state`获取游戏的飞行载具数据
   - 数据格式：JSON
   - 获取频率：每 0.1 秒一次

2. **关键数据字段**
   陆战载具数据：
   - `crew_total`: 总成员数
   - `crew_current`: 当前存活成员数
   - `driver_state`: 驾驶员状态 (1=存活，0=阵亡)
   - `gunner_state`: 炮手状态 (1=存活，0=阵亡)
   飞行载具数据：
   - `Ny`: 飞机过载度
   


3. **计算逻辑**
   - `crew_deal` = crew_total - crew_current（阵亡成员数）
   - `vehicles_deal` = 1 当且仅当：
     * driver_state == 1（驾驶员存活）
     * gunner_state == 1（炮手存活）
     * crew_deal == 0（无成员阵亡）
     * 其他情况下 vehicles_deal = 0

4. **强度计算**
   陆战载具强度计算：
   - 通道 A 强度 (s_a) = base_s + (cd_a × crew_deal) + (vd_a × vehicles_deal)
   - 通道 B 强度 (s_b) = base_s + (cd_b × crew_deal) + (vd_b × vehicles_deal)
   其中：
   - base_s: 基础强度
   - cd_a/cd_b: 成员阵亡影响系数
   - vd_a/vd_b: 载具状态影响系数
   飞行载具强度计算：
   - 通道 A 强度 (s_a) = base_s + （Ny x fjgz）
   - 通道 B 强度 (s_b) = base_s + （Ny x fjgz）
   其中：
   - base_s: 基础强度
   - Ny: 飞机过载度
   - fjgz: 飞机过载影响系数

### 设备控制逻辑 (c2dglab.py)

1. **设备连接**
   - 自动连接到郊狼 3.0 设备
   - 连接失败时自动重试（最多 5 次，间隔 5 秒）

2. **强度控制**
   - 实时监控 s_a 和 s_b 的变化
   - 将强度值映射到 0-100 的范围
   - 自动更新设备的通道强度

3. **波形参数**
   - 默认设置：sync(1, 9, 20, 5, 35, 20)
   - 参数说明：[待补充具体波形参数含义]

## 配置参数说明

通过配置界面（config.pyw）可以调整以下参数：
1. **基础参数**
   - `base_s`: 基础强度值
   - `cd_a/cd_b`: 成员阵亡对 A/B 通道的影响系数
   - `vd_a/vd_b`: 载具状态对 A/B 通道的影响系数
   - `fjgz`: 飞机过载对 A/B 通道的影响系数

2. **实时状态**
   - `crew_deal`: 当前阵亡成员数
   - `vehicles_deal`: 载具状态标志（0 或 1）
   - `s_a/s_b`: 当前 A/B 通道的实际强度值
   

## 使用方法

### Windows 系统

双击运行 `点我启动.bat`，这将会：
1. 启动数据获取模块（后台运行）
2. 打开配置界面
3. 运行主程序

### Unix-like 系统

在终端中运行：
```bash
chmod +x run.sh
./run.sh
```

## 日志说明

- 主程序日志：
  * 设备连接状态
  * 强度更新记录
  * 错误信息

- 数据获取模块日志：
  * 数据获取状态
  * 计算结果
  * 错误信息

## 开发说明

- 使用 pyproject.toml 管理项目依赖
- 支持 Python 虚拟环境（.venv）
- 模块化设计，便于维护和扩展

## 注意事项

1. 确保游戏数据接口 (localhost:8111) 可访问
2. 检查设备连接状态
3. 定期查看日志以监控系统运行状态
4. 确保配置参数在合理范围内

## 许可证

[许可证信息待补充]