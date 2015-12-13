#include "teamstyle17.h"
#include <iostream>
#include <random>
#include <time.h>

using namespace std;

void AIMain() {
    // Write your AI codes here :-)
	srand(clock());
	int r = rand() % 5;
	if (r == 0) {
	//	UpdateMap();
	} else if (r == 1) {
	//	UpdateStatus();
	} else if (r == 2) {
		Move({ 2, 3, 3 });
	} else if (r == 3) {
		UseSkill(SkillType(rand() % kSkillTypes), { 2, 3, 3 }, rand() % 233);
	} else {
		UpgradeSkill(SkillType(rand() % kSkillTypes));
	}
}
