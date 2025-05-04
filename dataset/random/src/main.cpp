#include <iostream>
#include <cstdlib> // For atoi
#include <ilcplex/cpxconst.h>

#include "cpxmacro.h"
#include "problems/bin_packing.h"
#include "problems/multi_knapsack.h"
#include "problems/set_cover.h"

struct StrongBranchingScore {
    int var_index;
    double score;
};

int main(int argc, char *argv[]) {
    // if (argc != 2) {
    //     std::cerr << "Usage: " << argv[0] << " <size>\n";
    //     return 1;
    // }
    //
    // const int size = std::atoi(argv[1]);
    //
    // if (size <= 0) {
    //     std::cerr << "Error: Size must be a positive integer.\n";
    //     return 1;
    // }
    //
    // std::cout << "The size provided is: " << size << std::endl;
    //
    // return 0;

    constexpr int n_problems = 5;

    // Set cover
    constexpr std::pair<int, int> sets = {100, 300};
    constexpr std::pair<int, int> elements = {100, 400};
    const std::vector<Problem> sc = set_cover(n_problems, sets, elements);
    for (const auto &problem: sc) {
        problem.export_bin("out/set_cover");
    }
    std::cout << "Generated " << sc.size() << "/" << n_problems << " SC problems" << std::endl;

    // // Bin packing
    // constexpr std::pair<int, int> items = {5, 30};
    // constexpr std::pair<int, int> bins = {3, 9};
    // constexpr std::pair<double, double> bin_capacity = {10.0, 20.0};
    // constexpr std::pair<double, double> item_size = {1.0, 5.0};
    // const std::vector<Problem> bp = bin_packing(n_problems, items, bins, bin_capacity, item_size);
    // for (const auto &problem: bp) {
    //     problem.export_bin("out/bin_packing");
    // }
    // std::cout << "Generated " << bp.size() << "/" << n_problems << " BP problems" << std::endl;

    // Multiple knapsack
    // constexpr std::pair<int, int> items_kp = {70, 150};
    // constexpr std::pair<int, int> knapsacks = {10, 20};
    // constexpr std::pair<double, double> knapsack_capacity = {100.0, 150.0};
    // constexpr std::pair<double, double> item_profit = {10.0, 100.0};
    // constexpr std::pair<double, double> item_weight = {5.0, 30.0};
    // const std::vector<Problem> kp = multi_knapsack(n_problems, items_kp, knapsacks, knapsack_capacity, item_profit,
    //                                                item_weight);
    // for (const auto &problem: kp) {
    //     problem.export_bin("out/multi_knapsack");
    // }
    // std::cout << "Generated " << kp.size() << "/" << n_problems << " KP problems" << std::endl;
}
