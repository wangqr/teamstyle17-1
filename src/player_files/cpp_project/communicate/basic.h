// 在这里定义选手用到的结构体 & 参数设置

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
	SHEILD, // ?
	kSkillTypes
};

const char SkillName[kSkillTypes][10] = { // 上面东西的字符串
	"SHEILD"
};


struct Position {
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
