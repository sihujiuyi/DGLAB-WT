# data_fetcher.py

import requests
import time
import global_vars  # 导入全局变量模块

# 目标 URL
indicators_url = "http://localhost:8111/indicators"
state_url = "http://localhost:8111/state"  # 飞机状态数据URL

# 重复执行的间隔时间（秒）
interval = 0.1  # 每 0.1 秒执行一次

def fetch_aircraft_data():
    """从 localhost:8111/state 获取飞机过载度(Ny)数据"""
    try:
        # 发送 GET 请求
        response = requests.get(state_url)
        response.raise_for_status()  # 检查请求是否成功

        # 解析 JSON 数据
        data = response.json()

        # 提取 Ny (飞机过载度)
        ny = data.get("Ny", 0)  # 如果没有Ny数据，默认为0
        
        print(f"Extracted aircraft Ny: {ny}")
        return ny

    except requests.exceptions.RequestException as e:
        print(f"请求飞机状态数据失败: {e}")
        return 0
    except ValueError as e:
        print(f"解析飞机状态数据失败: {e}")
        return 0

def fetch_indicators_data():
    """从 localhost:8111/indicators 提取 crew_total, crew_current, driver_state, gunner_state"""
    try:
        # 发送 GET 请求
        response = requests.get(indicators_url)
        response.raise_for_status()  # 检查请求是否成功

        # 解析 JSON 数据
        data = response.json()

        # 提取 crew_total, crew_current, driver_state, gunner_state
        crew_total = data.get("crew_total")
        crew_current = data.get("crew_current")
        driver_state = data.get("driver_state")
        gunner_state = data.get("gunner_state")

        if (
            crew_total is not None
            and crew_current is not None
            and driver_state is not None
            and gunner_state is not None
        ):
            print(
                f"Extracted crew_total: {crew_total}, crew_current: {crew_current}, "
                f"driver_state: {driver_state}, gunner_state: {gunner_state}"
            )
            return crew_total, crew_current, driver_state, gunner_state
        else:
            print("缺少必要字段，请检查 JSON 数据。")
            return None, None, None, None

    except requests.exceptions.RequestException as e:
        print(f"请求JSON指标数据失败: {e}")
        return None, None, None, None
    except ValueError as e:
        print(f"解析JSON指标数据失败: {e}")
        return None, None, None, None

def update_strength_values(config, crew_total=None, crew_current=None, driver_state=None, gunner_state=None, ny=None):
    """统一更新强度值的函数，优化了配置文件的读写操作
    
    这个函数整合了原来分散在多个函数中的逻辑，主要优化包括：
    1. 减少配置文件的读写次数：只在值真正发生变化时才更新配置
    2. 统一处理飞行载具和陆战载具的逻辑
    3. 使用配置缓存机制，避免频繁的文件IO操作
    4. 返回一个布尔值表示配置是否发生了变化，用于控制保存频率
    
    参数:
        config (dict): 当前的配置字典
        crew_total (int, optional): 总乘员数
        crew_current (int, optional): 当前乘员数
        driver_state (int, optional): 驾驶员状态（0或1）
        gunner_state (int, optional): 炮手状态（0或1）
        ny (float, optional): 飞机过载度
    
    返回:
        bool: 如果配置发生了变化返回True，否则返回False
    """
    """统一更新强度值的函数，减少配置文件的读写次数"""
    config_changed = False
    
    if config["is_aircraft"] and ny is not None:
        # 飞行载具逻辑
        threshold = config["fjgz_threshold"]
        
        # 计算新的强度值 - 只有当ny超过阈值时才应用过载影响
        if ny > threshold:
            s_a = config["base_s"] + (ny * config["fjgz"])
            s_b = config["base_s"] + (ny * config["fjgz"])
            print(f"Applying overload effect - Ny {ny} exceeds threshold {threshold}")
        else:
            s_a = config["base_s"]
            s_b = config["base_s"]
            print(f"Ny {ny} below threshold {threshold}, using base strength")
        
        # 只有当值发生变化时才更新配置
        if config["s_a"] != s_a or config["s_b"] != s_b:
            config["s_a"] = s_a
            config["s_b"] = s_b
            config_changed = True
            print(f"Updated aircraft strength - s_a: {s_a}, s_b: {s_b}")
    
    else:
        # 陆战载具逻辑
        if crew_total is not None and crew_current is not None:
            # 计算 crew_deal
            crew_deal = crew_total - crew_current
            
            # 只有当值发生变化时才更新配置
            if config["crew_deal"] != crew_deal:
                config["crew_deal"] = crew_deal
                config_changed = True
                print(f"Updated crew_deal: {crew_deal}")
        
        if driver_state is not None and gunner_state is not None:
            # 判断条件：driver_state 和 gunner_state 均为 1，且 crew_deal 为 0
            vehicles_deal = 1 if (driver_state == 1 and gunner_state == 1 and config["crew_deal"] == 0) else 0
            
            # 只有当值发生变化时才更新配置
            if config["vehicles_deal"] != vehicles_deal:
                config["vehicles_deal"] = vehicles_deal
                config_changed = True
                print(f"Updated vehicles_deal: {vehicles_deal}")
        
        # 计算 s_a 和 s_b
        s_a = config["base_s"] + config["cd_a"] * config["crew_deal"] + config["vehicles_deal"] * config["vd_a"]
        s_b = config["base_s"] + config["cd_b"] * config["crew_deal"] + config["vehicles_deal"] * config["vd_b"]
        
        # 只有当值发生变化时才更新配置
        if config["s_a"] != s_a or config["s_b"] != s_b:
            config["s_a"] = s_a
            config["s_b"] = s_b
            config_changed = True
            print(f"Updated strength values - s_a: {s_a}, s_b: {s_b}")
    
    return config_changed

# 主逻辑
def run_data_fetcher():
    try:
        last_save_time = 0
        min_save_interval = 0.5  # 最小保存间隔（秒）
        
        while True:
            # 加载当前配置
            config = global_vars.load_config()
            config_changed = False
            
            # 根据配置选择处理逻辑
            if config["is_aircraft"]:
                # 飞行载具逻辑
                ny = fetch_aircraft_data()
                config_changed = update_strength_values(config, ny=ny)
            else:
                # 陆战载具逻辑
                crew_total, crew_current, driver_state, gunner_state = fetch_indicators_data()
                config_changed = update_strength_values(
                    config, 
                    crew_total=crew_total, 
                    crew_current=crew_current, 
                    driver_state=driver_state, 
                    gunner_state=gunner_state
                )
            
            # 只有在配置有变化且距离上次保存时间超过最小间隔时才保存
            current_time = time.time()
            if config_changed and (current_time - last_save_time) >= min_save_interval:
                global_vars.save_config(config)
                global_vars.reload_globals()
                last_save_time = current_time
                print("Configuration saved.")

            # 等待指定时间后再次执行
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Data fetcher stopped by user.")

if __name__ == "__main__":
    run_data_fetcher()