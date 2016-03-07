// 在这里定义一些选手将来会用到的辅助函数

#include "../communicate/basic.h"
#include <math.h>

double Distance(Position pos1, Position pos2) {
	double dx = fabs(pos1.x - pos2.x), dy = fabs(pos1.y - pos2.y), dz = fabs(pos1.z - pos2.z);
	return sqrt(dx * dx + dy * dy + dz * dz);
}

Position Displacement(Position src, Position des) {
	Position d = { des.x - src.x, des.y - src.y, des.z - src.z };
	return d;
}

double Norm(Position v) {
	return sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}

Position Scale(double n, Position v) {
	Position t = { v.x * n, v.y * n, v.z * n };
	return t;
}

double DotProduct(Position vec1, Position vec2) {
	return vec1.x * vec2.x + vec1.y * vec2.y + vec1.z * vec2.z;
}

Position CrossProduct(Position u, Position v) {  // 真的会有人用这种东西吗..
	Position ret;
	ret.x = u.y * v.z - u.z * v.y;
	ret.y = u.z * v.x - u.x * v.z;
	ret.z = u.x * v.y - u.y * v.x;
	return ret;
}

double PointLineDistance(Position point, Position line_point_1, Position line_point_2) {
	double a, b, c, p, S;  // 三边长,半周长, 面积
	a = Norm(Displacement(point, line_point_1));
	b = Norm(Displacement(point, line_point_2));
	c = Norm(Displacement(line_point_1, line_point_2));
	if (c == 0) return double(0);
	p = (a + b + c) / 2;
	S = sqrt(p * (p - a) * (p - b) * (p - c));
	return 2 * S / c;
}

