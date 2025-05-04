#include <iostream>
#include <vector>
#include <random>

#include "cpxmacro.h"
#include "utils.h"

// seed with 0 to get the same random numbers every time
static std::mt19937 gen(0); //NOLINT(*-msc51-cpp)

int generate_rnd(const int min, const int max) {
    std::uniform_int_distribution<> distrib(min, max);
    return distrib(gen);
}

double generate_rnd(const double min, const double max) {
    std::uniform_real_distribution<> distrib(min, max);
    return distrib(gen);
}