#ifndef UTILS_H
#define UTILS_H

#include <string>

struct Solution {
    double obj_val;
    std::vector<double> x;
};

struct Problem {
    std::string name;
    std::vector<char> types;
    std::vector<double> c;
    std::vector<std::vector<double> > A;
    std::vector<double> b;
    std::vector<double> lb;
    std::vector<double> ub;
    Solution solution;
};


int generate_random_int(int min, int max);

double generate_random_double(double min, double max);

void solve(Problem &problem);

#endif //UTILS_H
