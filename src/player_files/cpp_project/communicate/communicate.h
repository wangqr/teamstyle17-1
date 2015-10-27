// 声明与 Python 之间通信有关的函数

# ifndef COMMUNICATE_H_
# define COMMUNICATE_H_

#include "basic.h"

// 这里明确下来和 Python 间传递信息的函数有且仅有一个发送 + 接收字符串的函数

typedef char *(*ComFuncType)(char*);
extern ComFuncType Communicate; // 向平台发送一个 json 串并从平台接收一个 json 串

# endif
