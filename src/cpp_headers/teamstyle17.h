#ifndef _TEAMSTYLE17_H_INCLUDE
#define _TEAMSTYLE17_H_INCLUDE
#include <memory.h> // memcpy

struct GameInfo {
	// TODO
	int bar;
} INFO; // This is a global variable

GameInfo *GetInfo() { // It is ok if player ZUOSI and change something in the structure so I don't use const :-)
	extern void *(*PyUpdate)();   // This is a global variable in communicate.cpp
	const GameInfo *py_info = (GameInfo *) PyUpdate();

	//memcpy((void *)&INFO, (const void *)py_info, sizeof(GameInfo));   // copy game info from Platform (Python) to cpp local variable
	INFO = *py_info;
	return &INFO;
}

void Action1(int foo) {  // A model function..
	void SendAction(int);
	SendAction(foo);
}

#endif