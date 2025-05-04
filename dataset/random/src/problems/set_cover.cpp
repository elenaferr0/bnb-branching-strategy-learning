#include "problems/set_cover.h"

#include <iostream>
#include <string>
#include <utility>
#include <vector>

#include "problem.h"
#include "utils.h"

Problem generate_problem(const int id, const std::pair<int, int> &sets, const std::pair<int, int> &elements) {
    const int n_sets = generate_rnd(sets.first, sets.second);
    const int n_elements = generate_rnd(elements.first, elements.second);

    const std::vector<double> c(n_sets, 1.0);

    std::vector<std::vector<double> > A(n_elements, std::vector<double>(n_sets));
    for (int i = 0; i < n_elements; ++i) {
        for (int j = 0; j < n_sets; ++j) {
            A[i][j] = (generate_rnd(0.0, 1.0) < A_DENSITY) ? 1 : 0;
        }
    }

    // Ensure each element is covered by at least one set
    for (int i = 0; i < n_elements; ++i) {
        const int covering_set_index = generate_rnd(0, n_sets - 1);
        A[i][covering_set_index] = 1;
    }

    // adding more random values
    for (int i = 0; i < n_elements; ++i) {
        for (int j = 0; j < n_sets; ++j) {
            if (A[i][j] == 0 && generate_rnd(0.0, 1.0) < A_DENSITY) {
                A[i][j] = 1;
            }
        }
    }

    const std::vector<double> b(n_elements, 1.0);
    const std::vector<char> types(n_elements, 'G');

    const std::vector<double> ub(n_sets, 1.0);
    const std::vector<double> lb(n_sets, 0.0);

    Problem problem = {"random_SC_" + std::to_string(id), types, c, A, b, lb, ub};
    problem.solve();
    return problem;
}

std::vector<Problem> set_cover(const int n_problems, const std::pair<int, int> &sets,
                               const std::pair<int, int> &elements) {
    std::vector<Problem> problems;
    int generated_problems = 0;
    int attempts = 0;

    while (generated_problems < n_problems && attempts < n_problems * 1.25) {
        auto problem = generate_problem(generated_problems, sets, elements);
        if (problem.solution->feasible) {
            generated_problems++;
            problems.push_back(problem);
        }
        attempts++;
    }

    return problems;
}
