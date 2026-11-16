#pragma once

#include <string>

namespace cdperf::log {

void open(const std::wstring& path);
void line(const char* format, ...);

}  // namespace cdperf::log
