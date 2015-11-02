#include "teamstyle17.h"
#include <iostream>

using namespace std;

void AIMain() {
    // Write your AI codes here :-)
	auto map = UpdateMap();
	cout << map->elements_list_size << endl;
	cout << map->elements[0].type << endl;
	cout << map->my_team;
}
