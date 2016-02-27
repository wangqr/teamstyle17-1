// 在这里定义一些选手将来会用到的辅助函数

#include "../communicate/basic.h"
#include <math.h>

double Distance(Position pos1, Position pos2) {
	double dx = abs(pos1.x - pos2.x), dy = abs(pos1.y - pos2.y), dz = abs(pos1.z - pos2.z);
	return sqrt(dx * dx + dy * dy + dz * dz);
}

Position Displacement(Position src, Position des) {
	return{ des.x - src.x, des.y - src.y, des.z - src.z };
}

int UpgradeSkillPrice(SkillType skill, const PlayerStatus *status) {
	int ret = 0;
	if (skill == HEALTH_UP) {
		int level = status->skill_level[HEALTH_UP];
		ret = kBasicSkillPrice[HEALTH_UP];
		while (level > 0) {
			ret *= 2;
			--level;
		}
	} else {
		int sum_level = 0;
		for (int i = 0; i != kSkillTypes; ++i) {
			if (i == HEALTH_UP) {
				continue;
			}
			sum_level += status->skill_level[i];
		}

		ret = kBasicSkillPrice[skill];
		while (sum_level > 0) {
			ret *= 2;
			--sum_level;
		}
	}
	return ret;
}
