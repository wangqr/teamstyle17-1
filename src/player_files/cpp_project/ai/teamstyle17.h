// 在这里声明选手要用到的函数 & 引用 basic.h

#ifndef TEAMSTYLE17_H_
#define TEAMSTYLE17_H_

# include "../communicate/basic.h"

const MapInfo *UpdateMap();

const PlayerStatus *UpdateStatus();

void Move(Position des);

void UseSkill(SkillType skill, Position des = { -1, -1, -1 }); // des 仅对 teleport 适用

void UpgradeSkill(SkillType skill);

#endif
