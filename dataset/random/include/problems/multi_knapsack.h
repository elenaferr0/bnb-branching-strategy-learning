#ifndef MULTI_KNAPSACK_H
#define MULTI_KNAPSACK_H
#include <utility>
#include <vector>

#include "problem.h"

Problem generate_problem(int id, const std::pair<int, int> &items, const std::pair<int, int> &knapsacks,
                         const std::pair<double, double> &knapsack_capacity, const std::pair<double, double> &item_profit,
                         const std::pair<double, double> &item_weight);

std::vector<Problem> multi_knapsack(int n_problems, const std::pair<int, int> &items, const std::pair<int, int> &knapsacks,
                                    const std::pair<double, double> &knapsack_capacity, const std::pair<double, double> &item_profit,
                                    const std::pair<double, double> &item_weight);
#endif
