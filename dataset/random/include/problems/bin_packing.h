#ifndef BIN_PACKING_H
#define BIN_PACKING_H
#include <utility>
#include <vector>

#include "problem.h"

Problem generate_problem(int id, const std::pair<int, int> &items, const std::pair<int, int> &bins,
                         const std::pair<double, double> &bin_capacity, const std::pair<double, double> &item_size);

std::vector<Problem> bin_packing(int n_problems,
                                 const std::pair<int, int> &items,
                                 const std::pair<int, int> &bins,
                                 const std::pair<double, double> &bin_capacity,
                                 const std::pair<double, double> &item_size);
#endif //BIN_PACKING_H
