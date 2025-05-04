#include "problems/set_cover.h"

#include <string>
#include <utility>
#include <vector>

#include "utils.h"

Problem generate_problem(const int id, const std::pair<int, int> &sets, const std::pair<int, int> &elements) {
    const int n_sets = generate_random_int(sets.first, sets.second);
    const int n_elements = generate_random_int(elements.first, elements.second);

    const std::vector<double> c(n_sets, 1.0);

    std::vector<std::vector<double> > A(n_elements, std::vector<double>(n_sets));
    for (int i = 0; i < n_elements; ++i) {
        for (int j = 0; j < n_sets; ++j) {
            A[i][j] = (generate_random_double(0.0, 1.0) < A_DENSITY) ? 1 : 0;
        }
    }

    // Ensure each element is covered by at least one set
    for (int j = 0; j < n_sets; ++j) {
        double sum_of_column = 0;
        for (int i = 0; i < n_elements; ++i) {
            sum_of_column += A[i][j];
        }
        if (sum_of_column == 0) {
            const int i = generate_random_int(0, n_elements - 1);
            A[i][j] = 1;
        }
    }

    const std::vector<double> b(n_elements, 1.0);
    const std::vector<char> types(n_elements, 'G');

    const std::vector<double> ub(n_sets, 1.0);
    const std::vector<double> lb(n_sets, 0.0);

    Problem problem = {"random_SC_" + std::to_string(id), types, c, A, b, lb, ub};
    solve(problem);
    return problem;
}

std::vector<Problem> set_cover(const int n_problems, const std::pair<int, int> &sets,
                               const std::pair<int, int> &elements) {
    std::vector<Problem> problems;
    for (int i = 0; i < n_problems; ++i) {
        problems.push_back(generate_problem(i, sets, elements));
    }
    return problems;
}
