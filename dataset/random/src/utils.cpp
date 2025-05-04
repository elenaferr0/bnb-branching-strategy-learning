#include <iostream>
#include <vector>
#include <random>

#include "cpxmacro.h"
#include "utils.h"

static std::mt19937 gen(0); // seed with 0

int generate_random_int(const int min, const int max) {
    std::uniform_int_distribution<> distrib(min, max);
    return distrib(gen);
}

double generate_random_double(const double min, const double max) {
    std::uniform_real_distribution<> distrib(min, max);
    return distrib(gen);
}

void solve(Problem &problem) {
    int status;
    char errmsg[BUF_SIZE];

    DECL_ENV(env);
    DECL_PROB(env, lp, problem.name.c_str());
    // Set time limit
    CHECKED_CPX_CALL(CPXsetdblparam, env, CPX_PARAM_TILIM, 10);

    // add variables
    const size_t n_vars = problem.c.size();
    const std::vector<char> var_types(n_vars, CPX_BINARY);

    CHECKED_CPX_CALL(CPXnewcols, env, lp, n_vars, problem.c.data(), problem.lb.data(), problem.ub.data(),
                     var_types.data(),
                     nullptr);

    // add constraints
    const size_t n_constraints = problem.types.size();
    std::vector<int> rmatbeg(n_constraints, 0);
    std::vector<int> rmatind;
    std::vector<double> rmatval;
    std::vector<char> sense(n_constraints);
    const std::vector<double> rhs = problem.b;

    for (int i = 0; i < n_constraints; ++i) {
        sense[i] = problem.types[i];
        rmatbeg[i] = static_cast<int>(rmatind.size());
        for (size_t j = 0; j < problem.A[i].size(); ++j) {
            if (std::abs(problem.A[i][j]) > 1e-9) {
                // Avoid adding zero coefficients
                rmatind.push_back(static_cast<int>(j));
                rmatval.push_back(problem.A[i][j]);
            }
        }
    }

    CHECKED_CPX_CALL(CPXaddrows, env, lp, 0, n_constraints, rmatind.size(), rhs.data(), sense.data(), rmatbeg.data(),
                     rmatind.data(), rmatval.data(), nullptr, nullptr);

    // optimize
    CHECKED_CPX_CALL(CPXmipopt, env, lp);

    // get the solution
    const int sol_status = CPXgetstat(env, lp);
    if (sol_status == CPXMIP_OPTIMAL || sol_status == CPXMIP_OPTIMAL_TOL) {
        CHECKED_CPX_CALL(CPXgetobjval, env, lp, &problem.solution.obj_val);
        std::cout << "Objective function value: " << problem.solution.obj_val << std::endl;
    } else {
        // throw std::runtime_error("No optimal solution found for problem: " + problem.name);
        std::cerr << "No optimal solution for " + problem.name;
        return;
    }

    problem.solution.x = std::vector<double>(n_vars);
    CHECKED_CPX_CALL(CPXgetx, env, lp, problem.solution.x.data(), 0, n_vars - 1);

    if (lp != nullptr) {
        CPXfreeprob(env, &lp);
    }
    if (env != nullptr) {
        CPXcloseCPLEX(&env);
    }
}
