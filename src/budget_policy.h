#pragma once

#include <cstdint>

namespace cdperf {

constexpr uint64_t kBytesPerMebibyte = 1024ull * 1024ull;

constexpr uint64_t capped_budget(uint64_t reported_budget_bytes, uint64_t cap_bytes) {
    if (cap_bytes == 0 || reported_budget_bytes <= cap_bytes) return reported_budget_bytes;
    return cap_bytes;
}

}  // namespace cdperf
