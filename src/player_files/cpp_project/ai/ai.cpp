#include "teamstyle17.h"
#include <iostream>
#include <time.h>
#include <random>

using namespace std;

void AIMain() {
	int r = rand() % 5;
	if (r == 0) {
		UpdateMap();
	} else if (r == 1) {
		UpdateStatus();
	} else if (r == 2) {
		Move({ 2, 3, 3 });
	} else if (r == 3) {
		Position des = { 2, 3, 3 };
		UseSkill(SkillType(rand() % kSkillTypes), des);
	} else {
		UpgradeSkill(SkillType(rand() % kSkillTypes));
	}
}
