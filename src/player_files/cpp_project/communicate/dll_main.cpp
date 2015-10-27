// 启动 dll 的主函数

#include <stdio.h>
#include <stdlib.h>
#include "basic.h"
#include "communicate.h"

#ifdef _WIN32
#define DLLEXPORT extern "C" __declspec(dllexport)
#else
#define DLLEXPORT extern "C"
#endif

extern int AI_ID;

void AIMain();

DLLEXPORT void StartAI(ComFuncType communicate, int ai_id) {
	// 用它来启动 ai

	AI_ID = ai_id;
	Communicate = communicate;

	while (true) {
		AIMain();   // Start AI
	}
	_sleep(100);
}
