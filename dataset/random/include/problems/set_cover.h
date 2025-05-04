#ifndef SET_COVER_H
#define SET_COVER_H
#include <utility>
#include <vector>

#include "problem.h"

constexpr double A_DENSITY = 0.5;

Problem generate_problem(int id, const std::pair<int, int> &sets, const std::pair<int, int> &elements);
std::vector<Problem> set_cover(int n_problems, const std::pair<int, int> &sets, const std::pair<int, int> &elements);


#endif //SET_COVER_H
