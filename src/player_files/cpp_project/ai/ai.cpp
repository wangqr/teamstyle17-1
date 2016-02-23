#include "teamstyle17.h"
#include<random>

void AIMain() {
	int i = rand() % 5;
	const MapInfo *map = NULL;
	const PlayerStatus *status = NULL;
	switch (i) {
	case 0:map = UpdateMap(); break;
	case 1:status = UpdateStatus(); break;
	case 2:UseSkill(SkillType(rand() % kSkillTypes), { 2, 3, 3 }); break;
	case 3:UpgradeSkill(SkillType(rand() % kSkillTypes)); break;
	default:Move({ 6, 6, 6 });
	}
}
