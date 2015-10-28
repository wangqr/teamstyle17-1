// 在这里声明选手要用到的函数 & 引用 basic.h

#ifndef TEAMSTYLE17_H_
#define TEAMSTYLE17_H_

# include "../communicate/basic.h"

GameInfo *UpdateMap();

PlayerStatus *UpdateStatus();

void Move(int element_id, Position des);

void UseSkill(int element_id, SkillType skill, Position des);

void UpgradeSkill(SkillType skill);

#endif
