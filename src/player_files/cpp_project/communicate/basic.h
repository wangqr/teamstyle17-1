// 主要参数与结构体的定义

#ifndef BASIC_H_
#define BASIC_H_

struct Position {
	int x;
	int y;
	int z;
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

	VISION_UP,
	HEALTH_UP,

	kSkillTypes
};

const int kMaxSkillLevel = 5;

// 技能参数 TODO
const int kLongAttackDamage[kMaxSkillLevel] = { 0 };
const int kShortAttackDamage[kMaxSkillLevel] = { 0 };
const int kShieldTime[kMaxSkillLevel] = { 0 };
const int kTeleportMaxDistance[kMaxSkillLevel] = { 0 };
const int kVisionUpValue[kMaxSkillLevel] = { 0 };
const int kHealthUpValue = 2000;

const int kSkillCD[kSkillTypes] = { 0 };

// 基础技能升级开销
const int kBasicSkillPrice[kSkillTypes] = { 1, 1, 2, 2, 2, 1 };  // From ts17core/gamemain.py

struct Object {
	int id;
	ObjectType type;
	Position pos;
	int radius;
};

// 物体/地图参数
const int kFoodHealth = 10;

const int kMapSize = 10000;
const int kMaxObjectNumber = 10000;

struct MapInfo {
	int time;  // ?
	Object objects[kMaxObjectNumber];
	int objects_list_size;
};

struct PlayerStatus {  // 根据逻辑 getStatusJson
	int id;
	int health;
	int vision;
	int ability; // 技能点
	int skill_level[kSkillTypes];
};


#endif
