#include "settings.h"

#include <windows.h>

namespace cdperf {
namespace {

std::vector<std::pair<std::wstring, std::wstring>> read_section_pairs(const std::wstring& ini_path,
                                                                      const wchar_t* section) {
    std::vector<wchar_t> buffer(32768);
    const DWORD length =
        GetPrivateProfileSectionW(section, buffer.data(), static_cast<DWORD>(buffer.size()), ini_path.c_str());
    std::vector<std::pair<std::wstring, std::wstring>> pairs;
    for (const wchar_t* entry = buffer.data(); entry < buffer.data() + length && *entry; entry += wcslen(entry) + 1) {
        const std::wstring text(entry);
        if (text.front() == L';' || text.front() == L'#') continue;
        const size_t separator = text.find(L'=');
        if (separator == std::wstring::npos || separator == 0) continue;
        pairs.emplace_back(text.substr(0, separator), text.substr(separator + 1));
    }
    return pairs;
}

}  // namespace

Settings load_settings(const std::wstring& ini_path) {
    Settings settings;
    settings.local_budget_cap_mebibytes =
        GetPrivateProfileIntW(L"video_memory", L"local_budget_cap_mb", 0, ini_path.c_str());
    settings.environment = read_section_pairs(ini_path, L"environment");
    return settings;
}

}  // namespace cdperf
