#include <vector>
#include <string>

#include "utils.h"

Problem generate_problem(const int id, const std::pair<int, int> &items, const std::pair<int, int> &knapsacks,
                         const std::pair<double, double> &knapsack_capacity_range,
                         const std::pair<double, double> &item_profit_range,
                         const std::pair<double, double> &item_weight_range) {
    const int n_knapsacks = generate_random_int(knapsacks.first, knapsacks.second);
    const int n_items = generate_random_int(items.first, items.second);
    std::vector<double> knapsack_capacities(n_knapsacks);
    double avg_knapsack_capacity = 0.0;
    for (int j = 0; j < n_knapsacks; ++j) {
        knapsack_capacities[j] = generate_random_double(knapsack_capacity_range.first, knapsack_capacity_range.second);
        avg_knapsack_capacity += knapsack_capacities[j];
    }
    avg_knapsack_capacity /= n_knapsacks;

    std::vector<double> item_profits(n_items);
    for (int i = 0; i < n_items; ++i) {
        item_profits[i] = generate_random_double(item_profit_range.first, item_profit_range.second);
    }

    // try to generate items which tend to be smaller (helps generating feasible problems)
    std::vector<double> item_weights(n_items);
    double avg_item_weight = 0.0;
    for (int i = 0; i < n_items; ++i) {
        item_weights[i] = generate_random_double(item_weight_range.first,
                                                 std::max(item_weight_range.first, avg_knapsack_capacity * 0.7));
        avg_item_weight += item_weights[i];
    }

    const int n_vars = n_items * n_knapsacks; // x_ij
    std::vector<double> c(n_vars);
    for (int i = 0; i < n_items; ++i) {
        for (int j = 0; j < n_knapsacks; ++j) {
            c[i * n_knapsacks + j] = -item_profits[i]; // convert to minimization problem
        }
    }

    std::vector<std::vector<double> > A;
    std::vector<double> b;
    std::vector<char> types;

    // Knapsack capacity constraints
    for (int j = 0; j < n_knapsacks; ++j) {
        std::vector<double> row(n_vars, 0.0);
        for (int i = 0; i < n_items; ++i) {
            row[i * n_knapsacks + j] = item_weights[i];
        }
        A.push_back(row);
        b.push_back(knapsack_capacities[j]);
        types.push_back('L');
    }

    // Item selection constraints
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
    std::vector<Problem> problems(n_problems);
    int generated_problems = 0;
    int attempts = 0;

    while (generated_problems < n_problems && attempts < n_problems * 1.25) {
        auto problem = generate_problem(generated_problems, items, knapsacks, knapsack_capacity, item_profit,
                                        item_weight);
        if (problem.solution.feasible) {
            generated_problems++;
            problems.push_back(problem);
        }
        attempts++;
    }

    return problems;
}
