// 主要参数与结构体的定义，选手需要阅读

#ifndef BASIC_H_
#define BASIC_H_

#define INF_ 2147483647

const int kMapSize = 20000;
const int kMaxObjectNumber = 10000;
const int kMaxPlayerObjectNumber = 10;  // 实际上应该不会有那么多

const double kDeathRatio = 1.0 / 4;  // 当前生命值与历史最大生命值之比小于此值即告死亡
const double kEatableRatio = 5.0 / 6;  // 目标单位半径与自己单位半径的比值小于此值时可以食用
const double kDevourDamage = 1.0 / 3;
const int kMaxMoveSpeed = 100;  // 未使用 Dash 时的最大速度
const int kFoodHealth = 40;

struct Position {
	double x;
	double y;
	double z;
};

typedef Position Speed;

enum ObjectType {
	PLAYER,  // 玩家单位
	ENERGY,  // 能量源
	ADVANCED_ENERGY,  // 打开的光之隧道
	SOURCE,  // 可能会刷出光之隧道的固定点
	DEVOUR,  // 吞噬者
	BOSS,  // 目标生物
	kObjectTypes
};

enum SkillType {
	LONG_ATTACK,
	SHORT_ATTACK,
	SHIELD,
	DASH,

	VISION_UP,  // 被动技能
	HEALTH_UP,  // 非技能

	kSkillTypes
};

const int kMaxSkillLevel = 5;

// 技能参数
const int kLongAttackDamage[kMaxSkillLevel + 1] = { 0, 100, 200, 300, 400, 500 };
const int kLongAttackRange[kMaxSkillLevel + 1] = { 0, 2500, 3000, 3500, 4000, 4500 };
const int kLongAttackCastingTime = 10;  // 蓄力时间
const int kShortAttackDamage[kMaxSkillLevel + 1] = { 0, 500, 700, 900, 1100, 1300 };
const int kShortAttackRange[kMaxSkillLevel + 1] = { 0, 1000, 1200, 1400, 1600, 1800 };
const int kShieldTime[kMaxSkillLevel + 1] = { 0, 30, 45, 60, 75, 90};
const int kDashSpeed[kMaxSkillLevel + 1] = { 0, 20, 40, 60, 80, 100 };  // 使用加速后的速度增量
const int kDashTime[kMaxSkillLevel + 1] = { 0, 40, 40, 40, 40, 80 };
const int kVision[kMaxSkillLevel + 1] = { 5000, 6000, 7000, 8000, 9000, 10000 };
const int kHealthUpValue = 500;

const int kSkillCD[kSkillTypes] = { 80, 80, 100, 100, 0, 0 };
const int kSkillCost[kSkillTypes] = { 10, 50, 0, 40, 0, 0 };  // 技能使用开销
const int kBasicSkillPrice[kSkillTypes] = { 1, 1, 2, 1, 2, 1 };  // 基础技能升级开销

struct Object {  // 视野内物体的公开可见属性
	int id;
	int team_id;  // -2 表示中立单位，0 ~ n-1 是选手
	ObjectType type;
	Position pos;
	double radius;
	int shield_time;  // 距离该单位护盾结束的时间， 0 表示无护盾
	int long_attack_casting;  // 距离此单位发动的 Long Attack 蓄力时间结束剩余的时间，-1 表示未发动此技能
};

struct Map {
	int time;  // 当前的回合数，也可用 GetTime 查询
	Object objects[kMaxObjectNumber];  // 视野内的所有物体
	int objects_number;
};

struct PlayerObject {  // 己方单位的可见属性
	int id;
	int health;
	int max_health;
	int vision;
	double radius;
	Position pos;
	Speed speed;  // 当前移动速度
	int long_attack_casting;
	int shield_time;
	int dash_time;
	int ability;  // 技能点
	int skill_level[kSkillTypes];
	int skill_cd[kSkillTypes];  // -1 表示此技能不能使用，0 表示可用
};

struct Status {
	int team_id;  // 自己的队伍编号
	PlayerObject objects[kMaxPlayerObjectNumber];  // 自己所有单位的列表
	int objects_number;
};

#endif
