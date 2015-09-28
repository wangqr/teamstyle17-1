#include <stdio.h>
#include <stdlib.h>

#ifdef _WIN32
#define DLLEXPORT extern "C" __declspec(dllexport)
#else
#define DLLEXPORT extern "C"
#endif

int AI_ID;

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
	char *action = (char*)malloc(100 * sizeof(char));
	sprintf(action, "Test message (Sent by AI%d)", AI_ID);
	PyGetAction(action);
	free(action);
}


void UpdateInfo();
void AIMain();

DLLEXPORT void StartAI(GetActionFuncType py_get_action, UpdateFuncType py_update, int ai_id) {
	// Platform - AIProxy will use this function to start ai
	AI_ID = ai_id;

	InitFunctions(py_get_action, py_update);
	UpdateInfo();

	while (true) {
		AIMain();   // Start AI
		break;
	}
}
