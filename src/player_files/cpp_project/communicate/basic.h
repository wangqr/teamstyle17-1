// 在这里定义选手用到的结构体 & 参数设置 & 依然不知道现在有哪些选手可见的参数...

#ifndef BASIC_H_
#define BASIC_H_

const int kMaxSkillLevel = 5; // 同上

enum ElementType {
	PLAYER,
	FOOD,
	// 中立生物？ 刺球？
	kUnitTypes
};

enum SkillType {
	SHEILD, // 还有哪些技能？以及它们的名字？
	FIREBALL,
	kSkillTypes
};

const char SkillName[kSkillTypes][10] = { // 上面东西的字符串
	"SHEILD",
	"FIREBALL"
};


struct Position {  // 以及这个要改成 double...
	int x;
	int y;
	int z;
};

struct Element {
	int id;
	int team;
	ElementType type;
	Position pos;
	int radius;
};

struct SkillProperty {

};

struct Skill {
	SkillType type;
	int level;
	// int cd; 如果有的话..
};

struct PlayerStatus {
	int id;
	int health;
	// int max_health; 似乎应该是要给出来的数据吧..
	int vision;
	int ability;
	Skill skills[kSkillTypes];
};


const int kMaxElementNumber = 200; // 随手写的..

struct MapInfo {
	int my_team;
	// int time; 不返回当前时间很不科学..
	PlayerStatus my_status;
	Element elements[kMaxElementNumber];
	int elements_list_size;
};


#endif
