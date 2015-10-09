#ifndef _TEAMSTYLE17_H_INCLUDE
#define _TEAMSTYLE17_H_INCLUDE
#include <stdio.h>
#include <string.h> // strcpy

struct GameInfo {
	// TODO
	int bar;
} INFO; // Global variable

void LoadPyInfo(char *py_info) { // Json string to GameInfo ...
	// test
	printf("AI recieved a message: %s\n", py_info);
}

void UpdateInfo() {
	extern char *(*PyUpdate)();
	char *py_info = PyUpdate();
	LoadPyInfo(py_info);
}

void Action1(int foo) {  // A model function..
	void SendAction(int);
	SendAction(foo);
}

#endif