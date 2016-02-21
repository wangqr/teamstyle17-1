// 主要参数与结构体的定义

#ifndef BASIC_H_
#define BASIC_H_

const int kMaxSkillLevel = 5;
const int kMapSize = 10000;
const int kMaxObjectsNumber = 1000;

// 以下根据逻辑的代码 gamemain.py

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

// 技能参数
// int kSkillProperty[kSkillTypes][kMaxSkillLevel];

struct Position {
	int x;
	int y;
	int z;
};

struct Object {
	int id;  // 多个 object 可能共用一个 id
	ObjectType type;
	Position pos;
	int radius;
};

struct PlayerStatus { // 根据逻辑 getStatusJson
	int id;
	int health;
	int vision;
	int ability; // 技能点
	int skillLevel[kSkillTypes];
};


struct MapInfo {
	int player_id;
	int time;
	PlayerStatus player_status;
	Object objects[kMaxObjectsNumber];
	int objects_list_size;
};

#endif
