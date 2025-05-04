#include <vector>
#include <string>

#include "utils.h"

Problem generate_problem(const int id, const std::pair<int, int> &items, const std::pair<int, int> &knapsacks,
                         const std::pair<double, double> &knapsack_capacity,
                         const std::pair<double, double> &item_profit,
                         const std::pair<double, double> &item_weight) {
    const int n_knapsacks = generate_random_int(knapsacks.first, knapsacks.second);
    const int n_items = generate_random_int(items.first, items.second);
    std::vector<double> knapsack_capacities(n_knapsacks);
    for (int j = 0; j < n_knapsacks; ++j) {
        knapsack_capacities[j] = generate_random_double(knapsack_capacity.first, knapsack_capacity.second);
    }
    std::vector<double> item_profits(n_items);
    for (int i = 0; i < n_items; ++i) {
        item_profits[i] = generate_random_double(item_profit.first, item_profit.second);
    }
    std::vector<double> item_weights(n_items);
    for (int i = 0; i < n_items; ++i) {
        item_weights[i] = generate_random_double(item_weight.first, item_weight.second);
    }

    const int n_vars = n_items * n_knapsacks; // x_ij
    std::vector<double> c(n_vars);
    for (int i = 0; i < n_items; ++i) {
        for (int j = 0; j < n_knapsacks; ++j) {
            // convert this to minimization problem
            c[i * n_knapsacks + j] = -item_profits[i];
        }
    }

    std::vector<std::vector<double> > A;
    std::vector<double> b;
    std::vector<char> types;

    // Knapsack capacity constraints: sum_{i} w_ij * x_ij <= W_j for all j
    for (int j = 0; j < n_knapsacks; ++j) {
        std::vector<double> row(n_vars, 0.0);
        for (int i = 0; i < n_items; ++i) {
            row[i * n_knapsacks + j] = item_weights[i];
        }
        A.push_back(row);
        b.push_back(knapsack_capacities[j]);
        types.push_back('L');
    }

    // Item selection constraints: sum_{j} x_ij = 1 for all i
    for (int i = 0; i < n_items; ++i) {
        std::vector<double> row(n_vars, 0.0);
        for (int j = 0; j < n_knapsacks; ++j) {
            row[i * n_knapsacks + j] = 1.0;
        }
        A.push_back(row);
        b.push_back(1.0);
        types.push_back('E');
    }

    std::vector<double> lb(n_vars, 0.0);
    std::vector<double> ub(n_vars, 1.0);

    Problem problem = {"random_MKP_" + std::to_string(id), types, c, A, b, lb, ub};
    solve(problem);
    return problem;
}

std::vector<Problem> multi_knapsack(const int n_problems, const std::pair<int, int> &items,
                                    const std::pair<int, int> &knapsacks,
                                    const std::pair<double, double> &knapsack_capacity,
                                    const std::pair<double, double> &item_profit,
                                    const std::pair<double, double> &item_weight) {
    std::vector<Problem> problems;
    for (int i = 0; i < n_problems; ++i) {
        problems.push_back(generate_problem(i, items, knapsacks, knapsack_capacity, item_profit, item_weight));
    }
    return problems;
}
