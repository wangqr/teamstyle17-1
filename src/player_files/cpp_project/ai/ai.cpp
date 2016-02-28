#include "teamstyle17.h"
#include<random>

void AIMain() {
	int i = rand() % 9;
	const MapInfo *map = NULL;
	const PlayerStatus *status = NULL;
	switch (i) {
	case 0:map = GetMap(); break;
	case 1:status = GetStatus(-1); break;
	case 2:LongAttack(-1, 1); break;
	case 3:ShortAttack(-1); break;
	case 4:Shield(-1); break;
	case 5:Teleport(-1, { double(rand() % kMapSize), double(rand() % kMapSize), double(rand() % kMapSize) }); break;
	case 6:UpgradeSkill(-1, SkillType(rand() % kSkillTypes)); break;
	case 7:GetTime(); break;
	default:Move(-1, { double(rand() % kMapSize), double(rand() % kMapSize), double(rand() % kMapSize) });
	}
}
