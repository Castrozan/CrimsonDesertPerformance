#include <cstdio>
#include <random>

#include "budget_policy.h"

namespace {

int failures = 0;

void expect(bool condition, const char* rule, uint64_t budget, uint64_t cap, uint64_t result) {
    if (condition) return;
    ++failures;
    std::printf("FAIL %s: budget=%llu cap=%llu result=%llu\n", rule, static_cast<unsigned long long>(budget),
                static_cast<unsigned long long>(cap), static_cast<unsigned long long>(result));
}

}  // namespace

int main() {
    std::mt19937_64 generator(20261116);
    std::uniform_int_distribution<uint64_t> mebibytes(0, 16384);
    for (int iteration = 0; iteration < 100000; ++iteration) {
        const uint64_t budget = mebibytes(generator) * cdperf::kBytesPerMebibyte + generator() % cdperf::kBytesPerMebibyte;
        const uint64_t cap = iteration % 7 == 0 ? 0 : mebibytes(generator) * cdperf::kBytesPerMebibyte;
        const uint64_t result = cdperf::capped_budget(budget, cap);
        expect(result <= budget, "never raises the budget", budget, cap, result);
        expect(cap == 0 || result <= cap, "never exceeds a set cap", budget, cap, result);
        expect(cap != 0 || result == budget, "zero cap leaves the budget alone", budget, cap, result);
        expect(budget > cap || result == budget, "budget under the cap passes through", budget, cap, result);
    }
    std::printf("budget_policy_test: %s\n", failures == 0 ? "passed" : "FAILED");
    return failures == 0 ? 0 : 1;
}
