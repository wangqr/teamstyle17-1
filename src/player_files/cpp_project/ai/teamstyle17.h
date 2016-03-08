// 在这里声明选手要用到的函数，选手需要阅读

#ifndef TEAMSTYLE17_H_
#define TEAMSTYLE17_H_

#include "../communicate/basic.h"

// 查询指令
int GetTime();  // 查询当前游戏时间
const Map *GetMap();  // 获取视野内的单位信息
const Status *GetStatus();  // 获取己方单位的状态

// 行动指令
void Move(int user_id, Speed speed);  // 移动，参数是速度矢量
void LongAttack(int user_id, int target_id);
void ShortAttack(int user_id);
void Shield(int user_id);
void Dash(int user_id);
void HealthUp(int user_id);
void UpgradeSkill(int user_id, SkillType skill);

// 特殊指令，选手调试用
void PAUSE(); 
void CONTINUE();

// 其他
double Distance(Position pos1, Position pos2);
Position Displacement(Position src, Position des);  // 从 src 到 des 的位移矢量 (矢量差)
double Norm(Position vec);  // 矢量模长
Position Scale(double n, Position vec);  // 矢量缩放 n 倍 (矢量数乘)
double DotProduct(Position vec1, Position vec2);  // 矢量点乘
Position CrossProduct(Position vec1, Position vec2);  // 叉乘
double PointLineDistance(Position point, Position line_point_1, Position line_point_2);  // 计算空间点线距离

#endif
