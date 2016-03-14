// 声明与 Python 之间通信有关的函数

# ifndef COMMUNICATE_H_
# define COMMUNICATE_H_

#include "basic.h"

typedef char *(*ComFuncType)(char*);
extern ComFuncType Communicate;

# endif
