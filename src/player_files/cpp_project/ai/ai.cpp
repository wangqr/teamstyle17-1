#include "teamstyle17.h"

void AIMain() {
    // Write your AI codes here :-)
	Move(1, { 3, 4, 5 });
	UpdateMap();
	UpdateStatus();
	UseSkill(3, SHEILD, { 2, 3, 3 });
	UpgradeSkill(SHEILD);
}
