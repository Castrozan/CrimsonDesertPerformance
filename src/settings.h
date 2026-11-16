#pragma once

#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace cdperf {

struct Settings {
    uint64_t local_budget_cap_mebibytes = 0;
    std::vector<std::pair<std::wstring, std::wstring>> environment;
};

Settings load_settings(const std::wstring& ini_path);

}  // namespace cdperf
