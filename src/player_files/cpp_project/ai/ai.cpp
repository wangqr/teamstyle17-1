#include "teamstyle17.h"
#include <iostream>

using namespace std;

void AIMain() {
    // Write your AI codes here :-)
//	Move(1, { 3, 4, 5 });
	auto map = UpdateMap();
	cout << map->elements_list_size << endl;
	cout << map->elements[0].type << endl;
	cout << map->my_id;
//	UpdateStatus();
//	UseSkill(3, SHEILD, { 2, 3, 3 });
//	UpgradeSkill(SHEILD);
}
