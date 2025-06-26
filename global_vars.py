import json
import os
import threading

# 文件锁，用于防止多个进程同时写入配置文件
_file_lock = threading.Lock()

# 配置文件路径
CONFIG_FILE = 'config.json'

# 默认配置
DEFAULT_CONFIG = {
    "crew_deal": 1.0,
    "vehicles_deal": 0,
    "s_a": 25.0,
    "s_b": 25.0,
    "base_s": 20.0,
    "cd_a": 5.0,
    "cd_b": 5.0,
    "vd_a": 20.0,
    "vd_b": 20.0,
    "fjgz": 5.0,  # 飞机过载影响系数
    "fjgz_threshold": 3.0,  # 飞机过载影响系数触发阈值
    "is_aircraft": False  # 是否为飞行载具
}

def _ensure_config_file():
    """确保配置文件存在，如果不存在则创建"""
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)

def load_config():
    """从配置文件加载配置"""
    _ensure_config_file()
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件时出错: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """保存配置到文件"""
    with _file_lock:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

def update_config(key, value):
    """更新单个配置项"""
    config = load_config()
    config[key] = value
    save_config(config)

def update_multiple_config(updates):
    """更新多个配置项"""
    config = load_config()
    for key, value in updates.items():
        config[key] = value
    save_config(config)

# 加载初始配置
_config = load_config()

# 为了兼容现有代码，定义全局变量
crew_deal = _config.get("crew_deal", 1.0)
vehicles_deal = _config.get("vehicles_deal", 0)
s_a = _config.get("s_a", 25.0)
s_b = _config.get("s_b", 25.0)
base_s = _config.get("base_s", 20.0)
cd_a = _config.get("cd_a", 5.0)
cd_b = _config.get("cd_b", 5.0)
vd_a = _config.get("vd_a", 20.0)
vd_b = _config.get("vd_b", 20.0)
fjgz = _config.get("fjgz", 5.0)
fjgz_threshold = _config.get("fjgz_threshold", 3.0)
is_aircraft = _config.get("is_aircraft", False)

def reload_globals():
    """重新加载全局变量"""
    global crew_deal, vehicles_deal, s_a, s_b, base_s, cd_a, cd_b, vd_a, vd_b, fjgz, fjgz_threshold, is_aircraft
    _config = load_config()
    crew_deal = _config.get("crew_deal", 1.0)
    vehicles_deal = _config.get("vehicles_deal", 0)
    s_a = _config.get("s_a", 25.0)
    s_b = _config.get("s_b", 25.0)
    base_s = _config.get("base_s", 20.0)
    cd_a = _config.get("cd_a", 5.0)
    cd_b = _config.get("cd_b", 5.0)
    vd_a = _config.get("vd_a", 20.0)
    vd_b = _config.get("vd_b", 20.0)
    fjgz = _config.get("fjgz", 5.0)
    fjgz_threshold = _config.get("fjgz_threshold", 3.0)
    is_aircraft = _config.get("is_aircraft", False)