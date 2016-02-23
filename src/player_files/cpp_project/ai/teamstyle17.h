// 在这里声明选手要用到的函数

#ifndef TEAMSTYLE17_H_
#define TEAMSTYLE17_H_

#include "../communicate/basic.h"

// 查询指令
const MapInfo *UpdateMap();  // 获取视野内的单位信息
const PlayerStatus *UpdateStatus();  // 获取自己的状态

// 行动指令
void Move(Position des);  // 移动，参数是速度矢量? 可以有负值?
void UseSkill(SkillType skill, Position des = { -1, -1, -1 }); // des 仅对 teleport(目标位置) 和 long attack(方向矢量?) 适用
void UpgradeSkill(SkillType skill);

// 特殊指令
void PAUSE();  // 调试用

// 其他
double Distance(Position pos1, Position pos2);
Position Displacement(Position src, Position des);  // 从 src 到 des 的位移矢量 (矢量差)

#endif
