// 在这里定义一些选手将来会用到的辅助函数

#include "../communicate/basic.h"
#include<math.h>

double Distance(Position pos1, Position pos2) {
	double dx = abs(pos1.x - pos2.x), dy = abs(pos1.y - pos2.y), dz = abs(pos1.z - pos2.z);
	return sqrt(dx * dx + dy * dy + dz * dz);
}

Position Displacement(Position src, Position des) {
	return{ des.x - src.x, des.y - src.y, des.z - src.z };
}

int UpgradeSkillPrice(SkillType skill, const PlayerStatus *status) {
	// TODO 计算技能升级花销？ 
}
