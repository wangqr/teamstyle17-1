// 声明与 Python 之间通信有关的函数

# ifndef COMMUNICATE_H_
# define COMMUNICATE_H_

#include "basic.h"
#include "./picojson/picojson.h"  // json 的解析器

extern int AI_ID; // 实际上应该没用

typedef char *(*ComFuncType)(char*);
extern ComFuncType Communicate; // 向平台发送一个字符串并从平台接收一个字符串

# endif
