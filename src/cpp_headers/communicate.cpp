#ifdef _WIN32  // It is different between MSVC and other compilers
#define DLLEXPORT extern "C" __declspec(dllexport)
#else
#define DLLEXPORT extern "C"
#endif

struct Action {
	// TODO
	int foo;
};

struct GameInfo;

typedef void(*GetActionFuncType)(Action *);
GetActionFuncType PyGetAction;   // void PyGetAction(Action *act)

typedef void *(*UpdateFuncType)();
UpdateFuncType PyUpdate;   // void *PyUpdate()

void InitFunctions(GetActionFuncType py_get_action, UpdateFuncType py_update) {
	// init the two function pointers above (global variable)

	PyGetAction = py_get_action;
	PyUpdate = py_update;
}

void SendAction(int foo) {
	// Send Action to Python

	Action act = { foo };
	PyGetAction(&act);
}

GameInfo *GetInfo();
void AIMain();

DLLEXPORT void StartAI(GetActionFuncType py_get_action, UpdateFuncType py_update) {
	// Platform - AIProxy will use this function to start ai

	InitFunctions(py_get_action, py_update);
	GetInfo();   // Init global variable INFO
	while (true) {
		AIMain();   // Start AI
	}
}
