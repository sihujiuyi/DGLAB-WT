# ui.py

import tkinter as tk
from tkinter import ttk, font
import importlib
import global_vars  # 导入全局变量模块
import os

def calculate_values(*args):
    """
    根据输入值更新全局变量
    """
    try:
        # 获取输入值
        base_s_value = float(base_s_entry.get()) if base_s_entry.get() else 0
        cd_a_value = float(cd_a_entry.get()) if cd_a_entry.get() else 0
        cd_b_value = float(cd_b_entry.get()) if cd_b_entry.get() else 0
        vd_a_value = float(vd_a_entry.get()) if vd_a_entry.get() else 0
        vd_b_value = float(vd_b_entry.get()) if vd_b_entry.get() else 0
        fjgz_value = float(fjgz_entry.get()) if fjgz_entry.get() else 0
        fjgz_threshold_value = float(fjgz_threshold_entry.get()) if fjgz_threshold_entry.get() else 0
        is_aircraft_value = is_aircraft_var.get()

        # 更新配置文件中的值
        updates = {
            "base_s": base_s_value,
            "cd_a": cd_a_value,
            "cd_b": cd_b_value,
            "vd_a": vd_a_value,
            "vd_b": vd_b_value,
            "fjgz": fjgz_value,
            "fjgz_threshold": fjgz_threshold_value,
            "is_aircraft": is_aircraft_value
        }
        global_vars.update_multiple_config(updates)
        
        # 重新加载全局变量
        global_vars.reload_globals()

        # 更新显示
        base_s_label.config(text=f"基础强度")
        cd_a_label.config(text=f"成员死亡数乘区 通道A")
        cd_b_label.config(text=f"成员死亡数乘区 通道B")
        vd_a_label.config(text=f"载具被摧毁强度 通道A")
        vd_b_label.config(text=f"载具被摧毁强度 通道B")
    except ValueError:
        base_s_label.config(text="输入值无效，请检查输入")
        cd_a_label.config(text="成员死亡数乘区 通道A")
        cd_b_label.config(text="成员死亡数乘区 通道B")
        vd_a_label.config(text="载具被摧毁强度 通道A")
        vd_b_label.config(text="载具被摧毁强度 通道B")

# 创建主窗口
root = tk.Tk()
root.title("War Thunder X 郊狼 V3")
root.geometry("400x480")  # 调整窗口大小以适应新增的输入框

# 设置窗口居中对齐
window_width = 400
window_height = 480
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 加载字体
custom_font = font.Font(size=12)  # 使用系统默认字体

# 左侧区域：输入和计算
left_frame = ttk.Frame(root)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# 第一排：标题
title_label = ttk.Label(left_frame, text="War Thunder X 郊狼 V3", font=(custom_font.actual()["family"], 16))
title_label.pack(pady=10)

# 第二排：基础强度
base_s_frame = ttk.Frame(left_frame)
base_s_frame.pack(pady=5)

base_s_label = ttk.Label(base_s_frame, text="基础强度", font=custom_font)
base_s_label.pack(side=tk.LEFT, padx=5)

base_s_entry = ttk.Entry(base_s_frame, width=10, font=custom_font)
base_s_entry.insert(0, str(global_vars.base_s))  # 从 global_vars.py 中加载默认值
base_s_entry.pack(side=tk.LEFT, padx=5)
base_s_entry.bind("<KeyRelease>", calculate_values)  # 输入时自动计算

# 第三排：成员死亡数乘区 通道A
cd_a_frame = ttk.Frame(left_frame)
cd_a_frame.pack(pady=5)

cd_a_label = ttk.Label(cd_a_frame, text="成员死亡数乘区 通道A", font=custom_font)
cd_a_label.pack(side=tk.LEFT, padx=5)

cd_a_entry = ttk.Entry(cd_a_frame, width=10, font=custom_font)
cd_a_entry.insert(0, str(global_vars.cd_a))  # 从 global_vars.py 中加载默认值
cd_a_entry.pack(side=tk.LEFT, padx=5)
cd_a_entry.bind("<KeyRelease>", calculate_values)  # 输入时自动计算

# 第四排：成员死亡数乘区 通道B
cd_b_frame = ttk.Frame(left_frame)
cd_b_frame.pack(pady=5)

cd_b_label = ttk.Label(cd_b_frame, text="成员死亡数乘区 通道B", font=custom_font)
cd_b_label.pack(side=tk.LEFT, padx=5)

cd_b_entry = ttk.Entry(cd_b_frame, width=10, font=custom_font)
cd_b_entry.insert(0, str(global_vars.cd_b))  # 从 global_vars.py 中加载默认值
cd_b_entry.pack(side=tk.LEFT, padx=5)
cd_b_entry.bind("<KeyRelease>", calculate_values)  # 输入时自动计算

# 第五排：载具被摧毁强度 通道A
vd_a_frame = ttk.Frame(left_frame)
vd_a_frame.pack(pady=5)

vd_a_label = ttk.Label(vd_a_frame, text="载具被摧毁强度 通道A", font=custom_font)
vd_a_label.pack(side=tk.LEFT, padx=5)

vd_a_entry = ttk.Entry(vd_a_frame, width=10, font=custom_font)
vd_a_entry.insert(0, str(global_vars.vd_a))  # 从 global_vars.py 中加载默认值
vd_a_entry.pack(side=tk.LEFT, padx=5)
vd_a_entry.bind("<KeyRelease>", calculate_values)  # 输入时自动计算

# 第六排：载具被摧毁强度 通道B
vd_b_frame = ttk.Frame(left_frame)
vd_b_frame.pack(pady=5)

vd_b_label = ttk.Label(vd_b_frame, text="载具被摧毁强度 通道B", font=custom_font)
vd_b_label.pack(side=tk.LEFT, padx=5)

vd_b_entry = ttk.Entry(vd_b_frame, width=10, font=custom_font)
vd_b_entry.insert(0, str(global_vars.vd_b))  # 从 global_vars.py 中加载默认值
vd_b_entry.pack(side=tk.LEFT, padx=5)
vd_b_entry.bind("<KeyRelease>", calculate_values)  # 输入时自动计算

# 第七排：飞机过载影响系数
fjgz_frame = ttk.Frame(left_frame)
fjgz_frame.pack(pady=5)

fjgz_label = ttk.Label(fjgz_frame, text="飞机过载影响系数", font=custom_font)
fjgz_label.pack(side=tk.LEFT, padx=5)

fjgz_entry = ttk.Entry(fjgz_frame, width=10, font=custom_font)
fjgz_entry.insert(0, str(global_vars.fjgz))  # 从 global_vars.py 中加载默认值
fjgz_entry.pack(side=tk.LEFT, padx=5)
fjgz_entry.bind("<KeyRelease>", calculate_values)  # 输入时自动计算

# 第八排：飞机过载触发阈值
fjgz_threshold_frame = ttk.Frame(left_frame)
fjgz_threshold_frame.pack(pady=5)

fjgz_threshold_label = ttk.Label(fjgz_threshold_frame, text="飞机过载触发阈值", font=custom_font)
fjgz_threshold_label.pack(side=tk.LEFT, padx=5)

fjgz_threshold_entry = ttk.Entry(fjgz_threshold_frame, width=10, font=custom_font)
fjgz_threshold_entry.insert(0, str(global_vars.fjgz_threshold))  # 从 global_vars.py 中加载默认值
fjgz_threshold_entry.pack(side=tk.LEFT, padx=5)
fjgz_threshold_entry.bind("<KeyRelease>", calculate_values)  # 输入时自动计算

# 第九排：飞行载具模式
is_aircraft_frame = ttk.Frame(left_frame)
is_aircraft_frame.pack(pady=5)

is_aircraft_var = tk.BooleanVar(value=global_vars.is_aircraft)
is_aircraft_checkbox = ttk.Checkbutton(
    is_aircraft_frame, 
    text="飞行载具模式", 
    variable=is_aircraft_var,
    command=calculate_values,
    style='Custom.TCheckbutton'
)
is_aircraft_checkbox.pack(pady=5)

# 创建自定义样式
style = ttk.Style()
style.configure('Custom.TCheckbutton', font=custom_font)

# 运行主循环
root.mainloop()