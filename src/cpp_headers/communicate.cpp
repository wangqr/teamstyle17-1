#include <stdio.h>
#include <stdlib.h>

#ifdef _WIN32
#define DLLEXPORT extern "C" __declspec(dllexport)
#else
#define DLLEXPORT extern "C"
#endif

int AI_ID;
char ACTION[100];

struct GameInfo;

typedef void(*GetActionFuncType)(char*);
GetActionFuncType PyGetAction;   // void PyGetAction(char *action)

typedef char *(*UpdateFuncType)();
UpdateFuncType PyUpdate;   // char *PyUpdate()


void InitFunctions(GetActionFuncType py_get_action, UpdateFuncType py_update) {
	// init the two function pointers above (global variable)

	PyGetAction = py_get_action;
	PyUpdate = py_update;
}

void SendAction(int foo) {
	// Send Action to Python
	// test
	sprintf(ACTION, "Test message (Sent by AI%d)", AI_ID);
	PyGetAction(ACTION);
}


void UpdateInfo();
void AIMain();

DLLEXPORT void StartAI(GetActionFuncType py_get_action, UpdateFuncType py_update, int ai_id) {
	// Platform - AIProxy will use this function to start ai
	AI_ID = ai_id;

	InitFunctions(py_get_action, py_update);
	UpdateInfo();

	printf("AI %d start\n", AI_ID);
	while (true) {
		AIMain();   // Start AI
		break;
	}
	_sleep(100);
}
