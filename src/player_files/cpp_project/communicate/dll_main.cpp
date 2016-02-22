// 启动 dll 的主函数

#ifdef _WIN32

#define DLLEXPORT extern "C" __declspec(dllexport)
#include <windows.h>
#define SLEEP(x) Sleep(x)

#else
#define DLLEXPORT extern "C"
#include <unistd.h>
#define SLEEP(x) usleep((x) * 1000)

#endif

#include "basic.h"
#include "communicate.h"

ComFuncType Communicate;

void AIMain();

DLLEXPORT void StartAI(ComFuncType communicate, int ai_id) {

	Communicate = communicate;

	while (true) {
		AIMain();   // 启动 AI
	}

	SLEEP(100);
}
