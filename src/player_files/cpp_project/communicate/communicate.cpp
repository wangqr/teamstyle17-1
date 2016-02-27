// 跟通信有关的函数定义

#include <stdio.h>
#include <string.h>
#include <string>
#include "basic.h"
#include "communicate.h"

const int kMaxMessageLength = 10000;

MapInfo MAP_;
PlayerStatus STATUS_;

// 以下是平台用

void LoadMapInfo(char *info_str) {
	int st = 12, ed = 12, object_counter = 0; // 强行让 time 的字段长为 12
	sscanf(info_str, "%d", &MAP_.time);
	while (info_str[ed] != 0) {
		if (info_str[ed] == ';') {  // 不同 Object 的数据以 ';' 分隔
			info_str[ed] = 0;
			sscanf(info_str + st, "%d%d%d%d%d%d", &MAP_.objects[object_counter].id, &MAP_.objects[object_counter].type,
				&MAP_.objects[object_counter].pos.x, &MAP_.objects[object_counter].pos.y, &MAP_.objects[object_counter].pos.z,
				&MAP_.objects[object_counter].radius);
			++object_counter;
			st = ed + 1;
		}
		++ed;
	}
	if (ed > st) {
		sscanf(info_str + st, "%d%d%d%d%d%d", &MAP_.objects[object_counter].id, &MAP_.objects[object_counter].type,
			&MAP_.objects[object_counter].pos.x, &MAP_.objects[object_counter].pos.y, &MAP_.objects[object_counter].pos.z,
			&MAP_.objects[object_counter].radius);
		++object_counter;
	}
	MAP_.objects_list_size = object_counter;
}

void LoadPlayerStatus(char *status_str) {
	sscanf(status_str, "%d%d%d%d%d%d%d%d%d%d", &STATUS_.id, &STATUS_.health, &STATUS_.vision, &STATUS_.ability,
		&STATUS_.skill_level[0], &STATUS_.skill_level[1], &STATUS_.skill_level[2],
		&STATUS_.skill_level[3], &STATUS_.skill_level[4], &STATUS_.skill_level[5]);
}

// 以下是选手用

const MapInfo *UpdateMap() {
	char msg_send[kMaxMessageLength];
	sprintf(msg_send, "query_map");

	char msg_receive[kMaxMessageLength];
	strcpy(msg_receive, Communicate(msg_send));

	LoadMapInfo(msg_receive);
	return &MAP_;
}

const PlayerStatus *UpdateStatus() {
	char msg_send[kMaxMessageLength];
	sprintf(msg_send, "query_status");

	char msg_receive[kMaxMessageLength];
	strcpy(msg_receive, Communicate(msg_send));

	LoadPlayerStatus(msg_receive);
	return &STATUS_;
}

void Move(Position des) {
	char msg_send[kMaxMessageLength];
	sprintf(msg_send, "move %d %d %d", des.x, des.y, des.z);
	Communicate(msg_send);
}

void UseSkill(SkillType skill, Position des) {
	char msg_send[kMaxMessageLength];
	sprintf(msg_send, "use_skill %d %d %d %d", skill, des.x, des.y, des.z);
	Communicate(msg_send);
}

void UpgradeSkill(SkillType skill) {
	char msg_send[kMaxMessageLength];
	sprintf(msg_send, "upgrade_skill %d", skill);
	Communicate(msg_send);
}

void PAUSE() {
	char msg_send[kMaxMessageLength];
	sprintf(msg_send, "pause");
	Communicate(msg_send);
}
