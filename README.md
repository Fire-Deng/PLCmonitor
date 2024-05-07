# PLCmonitor
监听PLC指定地址，读取指定寄存器数值并转译为字符。
用Python写的：可以同时监听4个PLC地址，检测出变化时读取对应寄存器的值（Int16），并转译为高低位2字符（chars）。最终以日志方式记录下来。
主程序为：PLCmonitor
运行依赖如：requirements.txt
