#include "teamstyle17.h"
#include<random>

void AIMain() {
	int i = rand() % 8;
	const MapInfo *map = NULL;
	const PlayerStatus *status = NULL;
	switch (i) {
	case 0:map = UpdateMap(); break;
	case 1:status = UpdateStatus(-1); break;
	case 2:LongAttack(-1, 1); break;
	case 3:ShortAttack(-1); break;
	case 4:Shield(-1); break;
	case 5:Teleport(-1, { double(rand() % kMapSize), double(rand() % kMapSize), double(rand() % kMapSize) }); break;
	case 6:UpgradeSkill(-1, SkillType(rand() % kSkillTypes)); break;
	default:Move(-1, { double(rand() % kMapSize), double(rand() % kMapSize), double(rand() % kMapSize) });
	}
}
