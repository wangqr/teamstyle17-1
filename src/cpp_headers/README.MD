# C++ Headers

by Ma-Xujie

此处存放选手用 C++ 头文件和 C++ 中的通信接口文件:

- ai.cpp
- communicate.cpp
- teamstyle17.h

## 通信方式

选手代码编译成 dll 文件，由平台 AI Proxy 调用。

AI Proxy 将选手需要用到的函数在启动选手 AI 的线程封装好以后，用 Python ctypes 库中的 [CFUNCTYPE](https://docs.python.org/3.4/library/ctypes.html#ctypes.CFUNCTYPE) 类型转换为 C 函数指针并作为参数传入 dll 。

启动 dll 时使用传入的函数指针初始化 AI 要调用的各种函数。

此后选手即可直接调用 Python 中的函数。

（暂定，视情况调整）
