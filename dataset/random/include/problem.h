#ifndef PROBLEM_H
#define PROBLEM_H
#include <string>
#include <vector>

struct Solution {
    double obj_val;
    bool feasible;
    std::vector<double> x;
};

class Problem {
public:
    std::string name;
    std::vector<char> types;
    std::vector<double> c;
    std::vector<std::vector<double> > A;
    std::vector<double> b;
    std::vector<double> lb;
    std::vector<double> ub;
    Solution *solution;

    Problem(std::string name, const std::vector<char> &types, const std::vector<double> &c,
            const std::vector<std::vector<double> > &A, const std::vector<double> &b, const std::vector<double> &lb,
            const std::vector<double> &ub);

    Problem(const Problem &other);
    Problem &operator=(const Problem &other);

    ~Problem();

    void solve();

    void export_bin(const std::string &path) const;
};

#endif //PROBLEM_H
