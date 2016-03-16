// 跟通信有关的函数定义

#include <stdio.h>
#include <string.h>
#include <string>
#include "basic.h"
#include "communicate.h"

#pragma warning(disable : 4996)

const int kMaxMessageLength = 1000000;

Map MAP_;
Status STATUS_;

char msg_send[kMaxMessageLength];
char msg_receive[kMaxMessageLength];

// 以下是平台用

void LoadMapInfo(char *info_str) {
	int st = 0, ed = 0, object_counter = 0;
	while (info_str[ed] != 0) {
		if (info_str[ed] == ';') {  // 不同 Object 的数据以 ';' 分隔
			info_str[ed] = 0;
			Object *obj = &MAP_.objects[object_counter];
			sscanf(info_str + st, "%d%d%d%lf%lf%lf%lf%d%d", &obj->id, &obj->team_id, (int *) &obj->type,
				&obj->pos.x, &obj->pos.y, &obj->pos.z,
				&obj->radius, &obj->long_attack_casting, &obj->shield_time);
			if (obj->type == PLAYER && obj->team_id == -2) {
				obj->type = BOSS;  // 判断一个物体是 BOSS
			}
			++object_counter;
			st = ed + 1;
		} else if(info_str[ed] == '|') {
			info_str[ed] = 0;
			sscanf(info_str + st, "%d", &MAP_.time);
			st = ed + 1;
		}
		++ed;
	}
	MAP_.objects_number = object_counter;
}

void LoadPlayerStatus(char *status_str) {
	int st = 0, ed = 0, object_counter = 0;
	// printf("%s\n", status_str);
	while (status_str[ed] != 0) {
		if (status_str[ed] == ';') {  // 不同 Object 的数据以 ';' 分隔
			status_str[ed] = 0;
			PlayerObject *player = &STATUS_.objects[object_counter];
			sscanf(status_str + st, "%d%d%d%d%d%lf%lf%lf%lf%lf%lf%lf%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d", &player->id, &player->health,
				&player->max_health, &player->vision, &player->ability,
				&player->radius, &player->pos.x, &player->pos.y, &player->pos.z,
				&player->speed.x, &player->speed.y, &player->speed.z,
				&player->skill_level[0], &player->skill_level[1], &player->skill_level[2],
				&player->skill_level[3], &player->skill_level[4], &player->skill_level[5],
				&player->skill_cd[0], &player->skill_cd[1], &player->skill_cd[2],
				&player->skill_cd[3], &player->skill_cd[4], &player->skill_cd[5],
				&player->long_attack_casting, &player->shield_time, &player->dash_time);
			++object_counter;
			st = ed + 1;
		} else if (status_str[ed] == '|') {
			status_str[ed] = 0;
			sscanf(status_str + st, "%d", &STATUS_.team_id);
			st = ed + 1;
		}
		++ed;
	}
	STATUS_.objects_number = object_counter;
}

void UseSkill(SkillType skill, int user_id, int target_id, Position des) { // 选手并不需要使用这个方法
	sprintf(msg_send, "use_skill %d %d %d %.10f %.10f %.10f", skill, user_id, target_id, des.x, des.y, des.z);
	Communicate(msg_send);
}

// 以下是选手用

const Map *GetMap() {
	sprintf(msg_send, "query_map");
	strcpy(msg_receive, Communicate(msg_send));
	LoadMapInfo(msg_receive);
	return &MAP_;
}

const Status *GetStatus() {
	sprintf(msg_send, "query_status %d", -1);
	strcpy(msg_receive, Communicate(msg_send));
	LoadPlayerStatus(msg_receive);
	return &STATUS_;
}

int GetTime() {
	sprintf(msg_send, "query_time");
	strcpy(msg_receive, Communicate(msg_send));
	int current_time;
	sscanf(msg_receive, "%d", &current_time);
	return current_time;
}

void Move(int user_id, Speed speed) {
	sprintf(msg_send, "move %d %.10f %.10f %.10f", user_id, speed.x, speed.y, speed.z);
	Communicate(msg_send);
}

void LongAttack(int user_id, int target_id) {
	Position tmp = { -1, -1, -1 };
	UseSkill(LONG_ATTACK, user_id, target_id, tmp);
}

void ShortAttack(int user_id) {
	Position tmp = { -1, -1, -1 };
	UseSkill(SHORT_ATTACK, user_id, -1, tmp);
}

void Shield(int user_id) {
	Position tmp = { -1, -1, -1 };
	UseSkill(SHIELD, user_id, -1, tmp);
}

void Dash(int user_id) {
	Position tmp = { -1, -1, -1 };
	UseSkill(DASH, user_id, -1, tmp);
}

void UpgradeSkill(int user_id, SkillType skill) {
	sprintf(msg_send, "upgrade_skill %d %d", skill, user_id);
	Communicate(msg_send);
}

void HealthUp(int user_id) {
	UpgradeSkill(user_id, HEALTH_UP);
}

void PAUSE() {
	sprintf(msg_send, "pause");
	Communicate(msg_send);
}

void CONTINUE() {
	PAUSE();  // 实际上和 PAUSE 的指令是一样的...
}
