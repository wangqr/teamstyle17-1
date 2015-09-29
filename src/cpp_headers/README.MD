# C++ Headers

by Ma-Xujie

此处存放选手用 C++ 头文件和 C++ 中的通信接口文件:

- ai.cpp
- communicate.cpp
- teamstyle17.h
- ai_test.dll --> 一个已经编译好用来测试通信的 dll 文件

## 通信方式

选手代码编译成 dll 文件，由平台 AI Proxy 调用。

AI Proxy 将选手需要用到的函数在启动选手 AI 的线程封装好以后，用 Python ctypes 库中的 [CFUNCTYPE](https://docs.python.org/3.4/library/ctypes.html#ctypes.CFUNCTYPE) 转换为 C 函数指针并作为参数传入 dll 。

启动 dll 时使用传入的函数指针初始化 AI 要调用的各种函数。

此后选手即可直接调用 Python 中的函数。

选手的指令与地图信息将以 json 字符串的形式传递

在 C++ 中对 json 串进行处理（暂定）

# 已经发现的坑

- 需要注意 MSVC 默认编译 32 位 dll，似乎只能用 32 位 Python 运行
- 如果两个 dll 文件名相同，会出现函数调用冲突。所以不能允许相同名称的 dll 同时运行
- 传入字符串时似乎会传错（概率极小）？ 
