#include <windows.h>

#include <cwchar>
#include <string>

#include "budget_policy.h"
#include "log.h"
#include "settings.h"
#include "video_memory_hook.h"

namespace {

std::wstring module_directory(HMODULE module) {
    wchar_t path[MAX_PATH];
    const DWORD length = GetModuleFileNameW(module, path, MAX_PATH);
    if (length == 0 || length == MAX_PATH) return L".";
    std::wstring text(path, length);
    return text.substr(0, text.find_last_of(L"\\/"));
}

bool is_game_process() {
    wchar_t path[MAX_PATH];
    const DWORD length = GetModuleFileNameW(nullptr, path, MAX_PATH);
    if (length == 0 || length == MAX_PATH) return false;
    const wchar_t* name = wcsrchr(path, L'\\');
    name = name ? name + 1 : path;
    return _wcsicmp(name, L"CrimsonDesert.exe") == 0 || GetEnvironmentVariableW(L"CDPERF_TEST_HOST", nullptr, 0) > 0;
}

cdperf::Settings settings;

DWORD WINAPI install_hooks(LPVOID) {
    cdperf::video_memory_hook::install(settings.local_budget_cap_mebibytes * cdperf::kBytesPerMebibyte);
    return 0;
}

void start(HMODULE module) {
    const std::wstring directory = module_directory(module);
    cdperf::log::open(directory + L"\\cdperf.log");
    cdperf::log::line("cdperf " CDPERF_VERSION " loaded");
    settings = cdperf::load_settings(directory + L"\\cdperf.ini");
    for (const auto& [name, value] : settings.environment) {
        SetEnvironmentVariableW(name.c_str(), value.c_str());
        cdperf::log::line("environment %ls=%ls", name.c_str(), value.c_str());
    }
    if (settings.local_budget_cap_mebibytes == 0) return;
    const HANDLE thread = CreateThread(nullptr, 0, install_hooks, nullptr, 0, nullptr);
    if (thread) CloseHandle(thread);
}

}  // namespace

BOOL APIENTRY DllMain(HMODULE module, DWORD reason, LPVOID) {
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(module);
        if (is_game_process()) start(module);
    }
    return TRUE;
}
