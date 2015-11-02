// 跟通信有关的函数定义 & json 解析

#include <stdio.h>  // sprintf
#include <string.h>
#include <string>
#include "basic.h"
#include "communicate.h"

const int kMaxMessageLength = 200;

MapInfo MAP;
PlayerStatus STATUS;

// 以下是平台用

void SetElement(int index, picojson::object &obj) {
	MAP.elements[index].id = obj["id"].get<double>();
	MAP.elements[index].radius = obj["r"].get<double>();

	std::string type = obj["type"].get<std::string>();
	if (type == "food") MAP.elements[index].type = FOOD;
	if (type == "player") MAP.elements[index].type = PLAYER; // ...

	picojson::array pos = obj["pos"].get<picojson::array>();
	MAP.elements[index].pos.x = pos[0].get<double>();
	MAP.elements[index].pos.y = pos[1].get<double>();
	MAP.elements[index].pos.z = pos[2].get<double>();
}

void LoadMapInfo(const char *info_str) { // 解析
	picojson::value val;
	picojson::parse(val, info_str);

	picojson::array objects = val.get("objects").get<picojson::array>();

	MAP.elements_list_size = objects.size();

	picojson::array::iterator it = objects.begin();
	while (it != objects.end()) {
		picojson::object obj = it->get<picojson::object>();
		SetElement(it - objects.begin(), obj);
		++it;
	}
}

void LoadPlayerStatus(const char *status_str) {
	// TODO
}


// 以下是选手用，ai_id 会在平台 AI Proxy 中填写，time 在平台主进程中填写

const MapInfo *UpdateMap() {
	char msg_send[kMaxMessageLength];
	sprintf(msg_send, "query_map");

	char msg_receive[kMaxMessageLength];
	strcpy(msg_receive, Communicate(msg_send) + 8);

	LoadMapInfo(msg_receive);
	return &MAP;
}

const PlayerStatus *UpdateStatus() {
	char msg_send[kMaxMessageLength];
	sprintf(msg_send, "query_status");

	char msg_receive[kMaxMessageLength];
	strcpy(msg_receive, Communicate(msg_send) + 8);

	LoadPlayerStatus(msg_receive);
	return &STATUS;
}

void Move(Position des) {
	char msg_send[kMaxMessageLength];
	sprintf(msg_send, "move %d %d %d", des.x, des.y, des.z);
	Communicate(msg_send);
}

void UseSkill(SkillType skill, Position des, int target=0) {
	char msg_send[kMaxMessageLength];
	sprintf(msg_send, "use_skill %s %d %d %d %d", SkillName[skill], des.x, des.y, des.z, target);
	Communicate(msg_send);
}

void UpgradeSkill(SkillType skill) {
	char msg_send[kMaxMessageLength];
	sprintf(msg_send, "upgrade_skill %s", SkillName[skill]);
	Communicate(msg_send);
}

