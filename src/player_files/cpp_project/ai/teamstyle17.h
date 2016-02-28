// 在这里声明选手要用到的函数

#ifndef TEAMSTYLE17_H_
#define TEAMSTYLE17_H_

#include "../communicate/basic.h"

// 查询指令
const MapInfo *UpdateMap();  // 获取视野内的单位信息
const PlayerStatus *UpdateStatus(int user_id = -1);  // 获取自己的状态

// 行动指令
void Move(int user_id, Position des);  // 移动，参数是速度矢量
void LongAttack(int user_id, int target_id);
void ShortAttack(int user_id);
void Shield(int user_id);
void Teleport(int user_id, Position des);
void HealthUp(int user_id);
void UpgradeSkill(int user_id, SkillType skill);

// 特殊指令
void PAUSE();  // 调试用
void CONTINUE();

// 其他
double Distance(Position pos1, Position pos2);
Position Displacement(Position src, Position des);  // 从 src 到 des 的位移矢量 (矢量差)

#endif
