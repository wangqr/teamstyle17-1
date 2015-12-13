// 在这里声明选手要用到的函数 & 引用 basic.h

#ifndef TEAMSTYLE17_H_
#define TEAMSTYLE17_H_

# include "../communicate/basic.h"

const MapInfo *UpdateMap();

const PlayerStatus *UpdateStatus();

void Move(Position des);

void UseSkill(SkillType skill, Position des, int target);

void UpgradeSkill(SkillType skill);

#endif
