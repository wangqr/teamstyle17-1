// 跟通信有关的函数定义 & json 解析

#include <stdio.h>  // sprintf
#include "basic.h"
#include "communicate.h"
#include "./picojson/picojson.h"  // json 的解析器

// 以下是平台用

GameInfo *LoadGameInfo(char *info_str) { // 解析
	return NULL;
}

PlayerStatus *LoadPlayerStatus(char *status_str) {
	return NULL;
}


// 以下是选手用，具体定义由发送的 json 串格式来决定

GameInfo *UpdateMap() {
	return NULL;
}

PlayerStatus *UpdateStatus() {
	return NULL;
}

void Move(int element_id, Position des) {

}

void UseSkill(int element_id, SkillType skill, Position des) {

}

void UpdateSkill(SkillType skill) {

}

