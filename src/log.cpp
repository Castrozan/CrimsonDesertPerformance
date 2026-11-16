#include "log.h"

#include <windows.h>

#include <cstdarg>
#include <cstdio>
#include <mutex>

namespace cdperf::log {
namespace {

std::mutex file_mutex;
FILE* file = nullptr;

}  // namespace

void open(const std::wstring& path) {
    std::lock_guard lock(file_mutex);
    if (file) return;
    file = _wfsopen(path.c_str(), L"w", _SH_DENYWR);
}

void line(const char* format, ...) {
    std::lock_guard lock(file_mutex);
    if (!file) return;
    SYSTEMTIME now;
    GetLocalTime(&now);
    std::fprintf(file, "[%02u:%02u:%02u.%03u] ", now.wHour, now.wMinute, now.wSecond, now.wMilliseconds);
    va_list arguments;
    va_start(arguments, format);
    std::vfprintf(file, format, arguments);
    va_end(arguments);
    std::fputc('\n', file);
    std::fflush(file);
}

}  // namespace cdperf::log
