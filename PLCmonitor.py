import tkinter as tk
from tkinter import ttk, messagebox
from pymodbus.client.sync import ModbusTcpClient
import datetime

# 创建主窗口
root = tk.Tk()
root.title("Modbus PLC 通信监控")
root.geometry("850x300")  # 更新窗口大小

# 添加标签和输入框
def create_label_entry(parent, label, row, col):
    ttk.Label(parent, text=label).grid(row=row, column=col, padx=5, pady=10, sticky="w")
    entry_var = tk.StringVar()
    entry = ttk.Entry(parent, textvariable=entry_var, width=15)
    entry.grid(row=row, column=col+1, padx=5, pady=10, sticky="w")
    return entry_var

ip_var = create_label_entry(root, "IP 地址:", 0, 0)
port_var = create_label_entry(root, "端口:", 0, 2)

listen_register_vars = []
read_register_start_vars = []
read_register_count_vars = []

status_label = tk.StringVar()
status_label.set("未监听")
tk.Label(root, textvariable=status_label, fg="red", font=("Helvetica", 12)).grid(row=6, column=2)

for i in range(4):
    base_row = i + 1
    listen_register_vars.append(create_label_entry(root, f"监听寄存器地址 {i+1}:", base_row, 0))
    read_register_start_vars.append(create_label_entry(root, f"读取寄存器开始地址 {i+1}:", base_row, 2))
    read_register_count_vars.append(create_label_entry(root, f"读取寄存器数量 {i+1}:", base_row, 4))

# 存储上次读取的值，初始化为空字典
last_values = {}

def monitor_registers():
    ip = ip_var.get()
    port = int(port_var.get())
    client = ModbusTcpClient(ip, port)
    
    if client.connect():
        status_label.set("正在监听")
        for index, (listen_var, read_start_var, read_count_var) in enumerate(zip(listen_register_vars, read_register_start_vars, read_register_count_vars)):
            listen_address = listen_var.get()
            if listen_address:
                listen_address = int(listen_address)
                response = client.read_holding_registers(address=listen_address, count=1, unit=1)
                if not response.isError():
                    current_value = response.registers[0]
                    # 判断监听地址值是否变化
                    if listen_address in last_values and current_value != last_values[listen_address]:
                        current_time = datetime.datetime.now()
                        filename = f"日志文件_{current_time.strftime('%Y-%m-%d')}.txt"
                        read_start_address = int(read_start_var.get())
                        read_count = int(read_count_var.get())
                        read_response = client.read_holding_registers(address=read_start_address, count=read_count, unit=1)
                        if not read_response.isError():
                            # 将读取的INT16整数转换为2个字符
                            chars = []
                            for num in read_response.registers:
                                high_byte = num >> 8  # 获取高8位
                                low_byte = num & 0xFF  # 获取低8位
                                chars.append(chr(low_byte))
                                chars.append(chr(high_byte))
                            read_values = ''.join(chars)
                        else:
                            read_values = "Error"
                        # 定义日志文本
                        #log_entry = f"{current_time} - Address {listen_address} Value Changed from {last_values[listen_address]} to {current_value}, Read Address {read_start_address} Values: {read_values}\n"
                        log_entry = f"{current_time} 地址:{listen_address}的值从{last_values[listen_address]}更改为 {current_value}, 输出地址 {read_start_address}及后{read_count}位的值是: {read_values}\n"
                        with open(filename, "a") as file:
                        # with open("register_change_log.txt", "a") as file:
                            file.write(log_entry)
                        # messagebox.showinfo("变化检测", f"寄存器地址 {listen_address} 值变化已记录")
                    last_values[listen_address] = current_value
        client.close()
    else:
        messagebox.showerror("连接失败", "无法连接到PLC")
        status_label.set("未监听")
        root.quit()
        
    root.after(1000, monitor_registers)  # 每1秒检查一次

submit_button = ttk.Button(root, text="开始监控", command=lambda: root.after(0, monitor_registers))
submit_button.grid(row=6, column=4, padx=10, pady=10, sticky="e")

# 运行主循环
root.mainloop()
