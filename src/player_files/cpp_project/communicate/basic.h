// 主要参数与结构体的定义

#ifndef BASIC_H_
#define BASIC_H_

#define INF_ 2147483647

const int kMapSize = 40000;
const int kMaxObjectNumber = 10000;
const int kMaxPlayerObjectNumber = 10;

const double kDeathRatio = 1 / 4;  // 当前生命值与历史最大生命值之比小于此值即告死亡
const double kEdibleRatio = 5 / 6;  // 目标单位半径与自己单位半径的比值小于此值时可以食用
const double kSpikeDamage = 1 / 3;
const int kMaxMoveSpeed = 0;
const int kFoodHealth = 10;


struct Position {
	double x;
	double y;
	double z;
};

enum ObjectType {
	PLAYER,
	FOOD,
	NUTRIENT,
	SPIKE,
	TARGET,
	BULLET,
	kObjectTypes
};

enum SkillType {
	LONG_ATTACK,
	SHORT_ATTACK,
	SHIELD,
	TELEPORT,

	VISION_UP,  // 被动技能
	HEALTH_UP,  // 非技能

	kSkillTypes
};

const int kMaxSkillLevel = 5;

// 技能参数 TODO
const int kLongAttackDamage[kMaxSkillLevel + 1] = { 0, 100, 200, 300, 400, 500 };
const int kLongAttackSpeed[kMaxSkillLevel + 1] = { 0, 100, 150, 200, 250, 300 };
const int kShortAttackDamage[kMaxSkillLevel + 1] = { 0, 1000, 1200, 1400, 1600, 1800 };
const int kShortAttackRange[kMaxSkillLevel + 1] = { 0, 100, 110, 120, 130, 140 };
const int kShieldTime[kMaxSkillLevel + 1] = { 0, 100, 120, 140, 160, 180 };
const int kTeleportMaxDistance[kMaxSkillLevel + 1] = { 0, 10000, 11000, 12000, 13000, INF_ };
const int kVisionUpValue[kMaxSkillLevel + 1] = { 0, 1000, 1500, 2000, 2500, 3000 };
const int kHealthUpValue = 2000;

const int kSkillCD[kSkillTypes] = { 80, 80, 100, 100, 0, 0 };
const int kSkillCost[kSkillTypes] = { 10, 50, 0, 0, 0, 0 };  // 技能使用开销

// 基础技能升级开销
const int kBasicSkillPrice[kSkillTypes] = { 1, 1, 2, 2, 2, 1 };

struct Object {
	int id;
	int ai_id;  // -2 表示中立单位，0 ~ n-1 是选手
	ObjectType type;
	Position pos;
	double radius;
	int shield_time;  // 0 表示无护盾
	int long_attack_casting;  // -1 表示未使用此技能， 大于等于 0 表示距离此技能命中自己的时间
};

struct MapInfo {
	int time;
	Object objects[kMaxObjectNumber];
	int objects_number;
};

struct PlayerObject {
	int id;
	int health;
	int max_health;
	int vision;
	double radius;
	Position pos;
	Position speed;
	int ability; // 技能点
	int skill_level[kSkillTypes];
	int skill_cd[kSkillTypes];  // -1 表示此技能不能使用
};

struct PlayerStatus {
	int ai_id;
	PlayerObject objects[kMaxPlayerObjectNumber];
	int objects_number;
};


#endif
