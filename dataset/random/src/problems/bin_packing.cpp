#include <iostream>
#include <ostream>
#include <string>
#include <vector>
#include "utils.h"

Problem generate_problem(const int id, const std::pair<int, int> &items, const std::pair<int, int> &bins,
                         const std::pair<double, double> &bin_capacity, const std::pair<double, double> &item_size) {
    const int n_items = generate_random_int(items.first, items.second);
    const int n_bins = generate_random_int(bins.first, bins.second);
    const double bin_capacity_val = generate_random_double(bin_capacity.first, bin_capacity.second);
    std::vector<double> item_sizes(n_items);
    for (int i = 0; i < n_items; ++i) {
        item_sizes[i] = generate_random_double(item_size.first, item_size.second);
    }
    const int n_vars = n_bins + n_items * n_bins; // y_j + x_{ij}

    std::vector<double> c(n_vars);
    for (int j = 0; j < n_bins; ++j) {
        c[j] = 1.0; // cost for bins (y_j)
    }
    for (int k = 0; k < n_items * n_bins; ++k) {
        c[n_bins + k] = 0.0; // no cost for x_{ij}
    }

    std::vector<std::vector<double> > A;
    std::vector<double> b;
    std::vector<char> types;

    // k >= 1
    std::vector<double> row_k_ge_1(n_vars, 0.0);
    for (int k = 0; k < n_items * n_bins; ++k) {
        row_k_ge_1[n_bins + k] = 1.0;
    }
    A.push_back(row_k_ge_1);
    b.push_back(1.0);
    types.push_back('G');

    // sum(s(i) * x_ij) <= B * y_j for all j
    for (int j = 0; j < n_bins; ++j) {
        std::vector<double> row_capacity(n_vars, 0.0);
        row_capacity[j] = -bin_capacity_val; // coefficient for y_j
        for (int i = 0; i < n_items; ++i) {
            row_capacity[n_bins + i * n_bins + j] = item_sizes[i]; // coefficient for x_{ij}
        }
        A.push_back(row_capacity);
        b.push_back(0.0);
        types.push_back('L');
    }

    // sum(x_ij) = 1 for all i
    for (int i = 0; i < n_items; ++i) {
        std::vector<double> row_item_assigned(n_vars, 0.0);
        for (int j = 0; j < n_bins; ++j) {
            row_item_assigned[n_bins + i * n_bins + j] = 1.0; // coefficient for x_{ij}
        }
        A.push_back(row_item_assigned);
        b.push_back(1.0);
        types.push_back('E');
    }

    std::vector<double> lb(n_vars, 0.0);
    std::vector<double> ub(n_vars, 1.0);

    Problem problem = {"randomBP_" + std::to_string(id), types, c, A, b, lb, ub};
    solve(problem);
    return problem;
}

std::vector<Problem> bin_packing(const int n_problems,
                                 const std::pair<int, int> &items,
                                 const std::pair<int, int> &bins,
                                 const std::pair<double, double> &bin_capacity,
                                 const std::pair<double, double> &item_size) {
    std::vector<Problem> problems(n_problems);
    int generated_problems = 0;
    int attempts = 0;

    while (generated_problems < n_problems && attempts < n_problems * 1.25) {
        auto problem = generate_problem(generated_problems, items, bins, bin_capacity, item_size);
        if (problem.solution.feasible) {
            generated_problems++;
            problems.push_back(problem);
        }
        attempts++;
    }

    return problems;
}
