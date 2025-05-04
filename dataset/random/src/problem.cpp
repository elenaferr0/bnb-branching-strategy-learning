#include "cpxmacro.h"
#include "problem.h"

#include <fstream>
#include <iostream>
#include <utility>

void Problem::solve() {
    int status;
    char errmsg[BUF_SIZE];

    DECL_ENV(env);
    DECL_PROB(env, lp, name.c_str());
    // Set time limit
    CHECKED_CPX_CALL(CPXsetdblparam, env, CPX_PARAM_TILIM, 5);
    // CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_MIPKAPPASTATS, 0);

    // Disable heuristics
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_HEURFREQ, -1);
    // Disable cuts
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_BQPCUTS, 0);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_CLIQUES, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_COVERS, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_DISJCUTS, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_FLOWCOVERS, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_FLOWPATHS, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_FRACCUTS, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_GUBCOVERS, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_IMPLBD, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_MIRCUTS, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_MCFCUTS, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_PROBE, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_RLTCUTS, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_LOCALIMPLBD, -1);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_ZEROHALFCUTS, -1);

    // Disable pre-solve
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_PREIND, CPX_OFF);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_REPEATPRESOLVE, 0);
    CHECKED_CPX_CALL(CPXsetintparam, env, CPX_PARAM_AGGIND, 0);

    // Set branching strategy
    CHECKED_CPX_CALL(CPXsetintparam, env, CPXPARAM_MIP_Strategy_VariableSelect, CPX_VARSEL_STRONG);

    // add variables
    const size_t n_vars = c.size();
    const std::vector<char> var_types(n_vars, CPX_BINARY);

    CHECKED_CPX_CALL(CPXnewcols, env, lp, n_vars, c.data(), lb.data(), ub.data(),
                     var_types.data(),
                     nullptr);

    // add constraints
    const size_t n_constraints = types.size();
    std::vector<int> rmatbeg(n_constraints, 0);
    std::vector<int> rmatind;
    std::vector<double> rmatval;
    std::vector<char> sense(n_constraints);
    const std::vector<double> rhs = b;

    for (int i = 0; i < n_constraints; ++i) {
        sense[i] = types[i];
        rmatbeg[i] = static_cast<int>(rmatind.size());
        for (size_t j = 0; j < A[i].size(); ++j) {
            if (std::abs(A[i][j]) > 1e-9) {
                // Avoid adding zero coefficients
                rmatind.push_back(static_cast<int>(j));
                rmatval.push_back(A[i][j]);
            }
        }
    }

    CHECKED_CPX_CALL(CPXaddrows, env, lp, 0, n_constraints, rmatind.size(), rhs.data(), sense.data(), rmatbeg.data(),
                     rmatind.data(), rmatval.data(), nullptr, nullptr);

    // optimize
    CHECKED_CPX_CALL(CPXmipopt, env, lp);

    // get the solution
    this->solution = new Solution();
    const int sol_status = CPXgetstat(env, lp);
    if (sol_status == CPXMIP_OPTIMAL || sol_status == CPXMIP_OPTIMAL_TOL) {
        CHECKED_CPX_CALL(CPXgetobjval, env, lp, &solution->obj_val);
        solution->feasible = true;
        solution->x = std::vector<double>(n_vars);
        CHECKED_CPX_CALL(CPXgetx, env, lp, solution->x.data(), 0, n_vars - 1);
    } else {
        // throw std::runtime_error("No optimal solution found for problem: " + name);
        solution->feasible = false;
    }

    if (lp != nullptr) {
        CPXfreeprob(env, &lp);
    }
    if (env != nullptr) {
        CPXcloseCPLEX(&env);
    }
}

void Problem::export_bin(const std::string &path) const {
    std::string filename = path + "/" + name + ".bin";
    std::cout << "File: " << filename << std::endl;
    std::ofstream outfile(filename, std::ios::binary);
    if (outfile.is_open()) {
        // Name
        int name_len = static_cast<int>(name.size());
        outfile.write(reinterpret_cast<const char *>(&name_len), sizeof(name_len));
        outfile.write(name.data(), name_len);

        // Types
        size_t types_size = types.size();
        outfile.write(reinterpret_cast<const char *>(&types_size), sizeof(types_size));
        outfile.write(types.data(), types_size * sizeof(char));

        // c
        size_t c_size = c.size();
        outfile.write(reinterpret_cast<const char *>(&c_size), sizeof(c_size));
        outfile.write(reinterpret_cast<const char *>(c.data()), c_size * sizeof(double));

        // A (number of rows, then for each row: number of cols, then elements)
        size_t num_rows_A = A.size();
        outfile.write(reinterpret_cast<const char *>(&num_rows_A), sizeof(num_rows_A));
        for (const auto &row: A) {
            size_t num_cols_row = row.size();
            outfile.write(reinterpret_cast<const char *>(&num_cols_row), sizeof(num_cols_row));
            outfile.write(reinterpret_cast<const char *>(row.data()), num_cols_row * sizeof(double));
        }

        // b (size followed by elements)
        size_t b_size = b.size();
        outfile.write(reinterpret_cast<const char *>(&b_size), sizeof(b_size));
        outfile.write(reinterpret_cast<const char *>(b.data()), b_size * sizeof(double));

        // lb (size followed by elements)
        size_t lb_size = lb.size();
        outfile.write(reinterpret_cast<const char *>(&lb_size), sizeof(lb_size));
        outfile.write(reinterpret_cast<const char *>(lb.data()), lb_size * sizeof(double));

        // ub (size followed by elements)
        size_t ub_size = ub.size();
        outfile.write(reinterpret_cast<const char *>(&ub_size), sizeof(ub_size));
        outfile.write(reinterpret_cast<const char *>(ub.data()), ub_size * sizeof(double));

        // Solution
        outfile.write(reinterpret_cast<const char *>(&solution->obj_val), sizeof(solution->obj_val));
        outfile.write(reinterpret_cast<const char *>(&solution->feasible), sizeof(solution->feasible));
        size_t x_size = solution->x.size();
        outfile.write(reinterpret_cast<const char *>(&x_size), sizeof(x_size));
        outfile.write(reinterpret_cast<const char *>(solution->x.data()), x_size * sizeof(double));

        outfile.close();
        std::cout << "Problem data exported to " << filename << " (binary format)" << std::endl;
    } else {
        std::cerr << "Unable to open file: " << filename << std::endl;
    }
}

Problem::Problem(std::string name, const std::vector<char> &types, const std::vector<double> &c,
                 const std::vector<std::vector<double> > &A, const std::vector<double> &b,
                 const std::vector<double> &lb,
                 const std::vector<double> &ub)
    : name(std::move(name)), types(types), c(c), A(A), b(b), lb(lb), ub(ub), solution(nullptr) {
}

Problem::~Problem() {
    delete solution;
}

Problem::Problem(const Problem &other) {
    name = other.name;
    types = other.types;
    c = other.c;
    A = other.A;
    b = other.b;
    lb = other.lb;
    ub = other.ub;

    solution = new Solution();
    solution->obj_val = other.solution->obj_val;
    solution->feasible = other.solution->feasible;
    solution->x = other.solution->x;
}

Problem &Problem::operator=(const Problem &other) {
    if (this == &other) {
        return *this;
    }

    delete solution;

    name = other.name;
    types = other.types;
    c = other.c;
    A = other.A;
    b = other.b;
    lb = other.lb;
    ub = other.ub;
    solution = new Solution();
    solution->obj_val = other.solution->obj_val;
    solution->feasible = other.solution->feasible;
    solution->x = other.solution->x;
    return *this;
}
