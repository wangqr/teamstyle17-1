#ifdef _WIN32
#define DLLEXPORT extern "C" __declspec(dllexport)
#else
#define DLLEXPORT extern "C"
#endif

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
	char *action = "Test Message";
	PyGetAction(action);
}


void UpdateInfo();
void AIMain();


DLLEXPORT void StartAI(GetActionFuncType py_get_action, UpdateFuncType py_update) {
	// Platform - AIProxy will use this function to start ai

	InitFunctions(py_get_action, py_update);
	UpdateInfo();

	while (true) {
		AIMain();   // Start AI
	}
}
