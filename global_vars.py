import json
import os
import threading
import tempfile
import shutil
from pathlib import Path

# 文件锁，用于防止多个进程同时写入配置文件
_file_lock = threading.Lock()

# 配置文件的备份路径
BACKUP_FILE = 'config.json.backup'

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

# 配置缓存和上次修改时间
_config_cache = None
_last_modified_time = 0

def _ensure_config_file():
    """确保配置文件存在，如果不存在则创建"""
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        # 创建备份
        shutil.copy2(CONFIG_FILE, BACKUP_FILE)

def _is_valid_json_file(file_path):
    """检查文件是否是有效的JSON文件"""
    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return False
        with open(file_path, 'r') as f:
            json.load(f)
        return True
    except Exception:
        return False

def load_config():
    """从配置文件加载配置，使用缓存减少文件读取"""
    global _config_cache, _last_modified_time
    
    # 确保配置文件存在
    _ensure_config_file()
    
    try:
        # 检查文件是否被修改
        current_mtime = os.path.getmtime(CONFIG_FILE)
        if _config_cache is not None and current_mtime <= _last_modified_time:
            # 使用缓存的配置
            return _config_cache.copy()
        
        # 检查配置文件是否有效
        if not _is_valid_json_file(CONFIG_FILE):
            print("配置文件无效或损坏，尝试恢复备份...")
            if _is_valid_json_file(BACKUP_FILE):
                shutil.copy2(BACKUP_FILE, CONFIG_FILE)
                print("已从备份恢复配置文件")
            else:
                print("备份文件也无效，使用默认配置")
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(DEFAULT_CONFIG, f, indent=4)
        
        # 加载配置
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # 更新缓存
        _config_cache = config.copy()
        _last_modified_time = current_mtime
        
        return config
    except Exception as e:
        print(f"加载配置文件时出错: {e}")
        if _config_cache is not None:
            print("使用缓存的配置")
            return _config_cache.copy()
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """安全地保存配置到文件，使用临时文件避免损坏"""
    global _config_cache, _last_modified_time
    
    with _file_lock:
        try:
            # 创建临时文件
            fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(CONFIG_FILE))
            try:
                with os.fdopen(fd, 'w') as temp_file:
                    json.dump(config, temp_file, indent=4)
                
                # 备份当前配置文件（如果存在且有效）
                if os.path.exists(CONFIG_FILE) and _is_valid_json_file(CONFIG_FILE):
                    shutil.copy2(CONFIG_FILE, BACKUP_FILE)
                
                # 安全地替换配置文件
                shutil.move(temp_path, CONFIG_FILE)
                
                # 更新缓存
                _config_cache = config.copy()
                _last_modified_time = os.path.getmtime(CONFIG_FILE)
            except Exception as e:
                # 如果出错，删除临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise e
        except Exception as e:
            print(f"保存配置文件时出错: {e}")

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

def _validate_config(config):
    """验证配置文件的完整性和类型"""
    required_fields = {
        "crew_deal": float,
        "vehicles_deal": int,
        "s_a": float,
        "s_b": float,
        "base_s": float,
        "cd_a": float,
        "cd_b": float,
        "vd_a": float,
        "vd_b": float,
        "fjgz": float,
        "fjgz_threshold": float,
        "is_aircraft": bool
    }
    
    # 检查所有必需字段
    for field, field_type in required_fields.items():
        if field not in config:
            print(f"配置缺少必需字段: {field}，使用默认值")
            config[field] = DEFAULT_CONFIG[field]
            continue
            
        # 检查字段类型
        try:
            if not isinstance(config[field], field_type):
                # 尝试转换类型
                config[field] = field_type(config[field])
        except (ValueError, TypeError):
            print(f"字段 {field} 的类型错误，使用默认值")
            config[field] = DEFAULT_CONFIG[field]
    
    return config

def reload_globals():
    """重新加载全局变量，使用缓存机制"""
    global crew_deal, vehicles_deal, s_a, s_b, base_s, cd_a, cd_b, vd_a, vd_b, fjgz, fjgz_threshold, is_aircraft
    
    # 使用缓存的配置（如果可用）
    if _config_cache is not None:
        _config = _config_cache.copy()
    else:
        _config = load_config()
    
    # 验证配置
    _config = _validate_config(_config)
    
    # 更新全局变量
    crew_deal = _config["crew_deal"]
    vehicles_deal = _config["vehicles_deal"]
    s_a = _config["s_a"]
    s_b = _config["s_b"]
    base_s = _config["base_s"]
    cd_a = _config["cd_a"]
    cd_b = _config["cd_b"]
    vd_a = _config["vd_a"]
    vd_b = _config["vd_b"]
    fjgz = _config["fjgz"]
    fjgz_threshold = _config["fjgz_threshold"]
    is_aircraft = _config["is_aircraft"]