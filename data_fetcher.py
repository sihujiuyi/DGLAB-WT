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

def update_aircraft_strength(ny):
    """更新飞机载具的强度值"""
    # 加载当前配置
    config = global_vars.load_config()
    
    # 获取阈值
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
    
    # 更新配置中的 s_a 和 s_b
    config["s_a"] = s_a
    config["s_b"] = s_b
    
    # 保存配置
    global_vars.save_config(config)
    
    # 重新加载全局变量
    global_vars.reload_globals()
    
    print(f"Updated aircraft strength - s_a: {s_a}, s_b: {s_b}")

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

def update_crew_deal(crew_total, crew_current):
    """更新全局变量 crew_deal 并写入配置文件"""
    if crew_total is not None and crew_current is not None:
        # 计算 crew_deal
        crew_deal = crew_total - crew_current
        
        # 加载当前配置
        config = global_vars.load_config()
        
        # 更新配置中的 crew_deal
        config["crew_deal"] = crew_deal
        
        # 计算 s_a 和 s_b
        s_a = config["base_s"] + config["cd_a"] * crew_deal + config["vehicles_deal"] * config["vd_a"]
        s_b = config["base_s"] + config["cd_b"] * crew_deal + config["vehicles_deal"] * config["vd_b"]
        
        # 更新配置中的 s_a 和 s_b
        config["s_a"] = s_a
        config["s_b"] = s_b
        
        # 保存配置
        global_vars.save_config(config)
        
        # 重新加载全局变量
        global_vars.reload_globals()
        
        print(f"Updated crew_deal: {crew_deal}, s_a: {s_a}, s_b: {s_b}")
    else:
        print("Failed to extract crew data.")

def update_vehicles_deal(driver_state, gunner_state):
    """更新全局变量 vehicles_deal 并写入配置文件"""
    if driver_state is not None and gunner_state is not None:
        # 加载当前配置
        config = global_vars.load_config()
        
        # 判断条件：driver_state 和 gunner_state 均为 1，且 crew_deal 为 0
        if driver_state == 1 and gunner_state == 1 and config["crew_deal"] == 0:
            vehicles_deal = 1
        else:
            vehicles_deal = 0
            
        # 更新配置中的 vehicles_deal
        config["vehicles_deal"] = vehicles_deal
        
        # 计算 s_a 和 s_b
        s_a = config["base_s"] + config["cd_a"] * config["crew_deal"] + vehicles_deal * config["vd_a"]
        s_b = config["base_s"] + config["cd_b"] * config["crew_deal"] + vehicles_deal * config["vd_b"]
        
        # 更新配置中的 s_a 和 s_b
        config["s_a"] = s_a
        config["s_b"] = s_b
        
        # 保存配置
        global_vars.save_config(config)
        
        # 重新加载全局变量
        global_vars.reload_globals()
        
        print(f"Updated vehicles_deal: {vehicles_deal}, s_a: {s_a}, s_b: {s_b}")
    else:
        print("Failed to extract driver_state or gunner_state.")

# 主逻辑
def run_data_fetcher():
    try:
        while True:
            # 加载当前配置
            config = global_vars.load_config()
            
            # 根据配置选择处理逻辑
            if config["is_aircraft"]:
                # 飞行载具逻辑
                ny = fetch_aircraft_data()
                update_aircraft_strength(ny)
            else:
                # 陆战载具逻辑
                crew_total, crew_current, driver_state, gunner_state = fetch_indicators_data()
                update_crew_deal(crew_total, crew_current)
                update_vehicles_deal(driver_state, gunner_state)

            # 等待指定时间后再次执行
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Data fetcher stopped by user.")

if __name__ == "__main__":
    run_data_fetcher()