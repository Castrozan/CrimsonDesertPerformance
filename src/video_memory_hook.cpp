#include "video_memory_hook.h"

#include <windows.h>
#include <dxgi1_4.h>

#include <atomic>

#include "budget_policy.h"
#include "log.h"

namespace cdperf::video_memory_hook {
namespace {

constexpr size_t kQueryVideoMemoryInfoSlot = 14;
constexpr ULONGLONG kLogIntervalMilliseconds = 30000;

using QueryVideoMemoryInfoFunction = HRESULT(STDMETHODCALLTYPE*)(IDXGIAdapter3*, UINT, DXGI_MEMORY_SEGMENT_GROUP,
                                                                 DXGI_QUERY_VIDEO_MEMORY_INFO*);

QueryVideoMemoryInfoFunction original_query = nullptr;
uint64_t budget_cap_bytes = 0;
std::atomic<uint64_t> call_count[2];
std::atomic<ULONGLONG> last_logged_tick[2];

void log_call(DXGI_MEMORY_SEGMENT_GROUP segment, uint64_t real_budget, const DXGI_QUERY_VIDEO_MEMORY_INFO& info) {
    const int index = segment == DXGI_MEMORY_SEGMENT_GROUP_LOCAL ? 0 : 1;
    const uint64_t calls = ++call_count[index];
    const ULONGLONG now = GetTickCount64();
    ULONGLONG previous = last_logged_tick[index].load();
    if (calls != 1 && now - previous < kLogIntervalMilliseconds) return;
    if (!last_logged_tick[index].compare_exchange_strong(previous, now)) return;
    log::line("QueryVideoMemoryInfo %s: calls %llu | budget real %llu MiB reported %llu MiB | usage %llu MiB",
              index == 0 ? "local" : "non-local", calls, real_budget / kBytesPerMebibyte,
              info.Budget / kBytesPerMebibyte, info.CurrentUsage / kBytesPerMebibyte);
}

HRESULT STDMETHODCALLTYPE query_with_cap(IDXGIAdapter3* adapter, UINT node_index, DXGI_MEMORY_SEGMENT_GROUP segment,
                                         DXGI_QUERY_VIDEO_MEMORY_INFO* info) {
    const HRESULT result = original_query(adapter, node_index, segment, info);
    if (FAILED(result) || !info) return result;
    const uint64_t real_budget = info->Budget;
    if (segment == DXGI_MEMORY_SEGMENT_GROUP_LOCAL) {
        info->Budget = capped_budget(real_budget, budget_cap_bytes);
        if (info->AvailableForReservation > info->Budget) info->AvailableForReservation = info->Budget;
    }
    log_call(segment, real_budget, *info);
    return result;
}

bool patch_slot(void** slot, void* replacement) {
    DWORD old_protection = 0;
    if (!VirtualProtect(slot, sizeof(void*), PAGE_READWRITE, &old_protection)) return false;
    *slot = replacement;
    VirtualProtect(slot, sizeof(void*), old_protection, &old_protection);
    return true;
}

}  // namespace

bool install(uint64_t local_budget_cap_bytes) {
    budget_cap_bytes = local_budget_cap_bytes;
    IDXGIFactory1* factory = nullptr;
    if (FAILED(CreateDXGIFactory1(__uuidof(IDXGIFactory1), reinterpret_cast<void**>(&factory)))) {
        log::line("video memory hook: CreateDXGIFactory1 failed");
        return false;
    }
    IDXGIAdapter1* adapter = nullptr;
    IDXGIAdapter3* adapter3 = nullptr;
    bool installed = false;
    if (SUCCEEDED(factory->EnumAdapters1(0, &adapter)) &&
        SUCCEEDED(adapter->QueryInterface(__uuidof(IDXGIAdapter3), reinterpret_cast<void**>(&adapter3)))) {
        void** vtable = *reinterpret_cast<void***>(adapter3);
        void** slot = &vtable[kQueryVideoMemoryInfoSlot];
        if (*slot == reinterpret_cast<void*>(&query_with_cap)) {
            installed = true;
        } else {
            original_query = reinterpret_cast<QueryVideoMemoryInfoFunction>(*slot);
            installed = patch_slot(slot, reinterpret_cast<void*>(&query_with_cap));
        }
        DXGI_QUERY_VIDEO_MEMORY_INFO info{};
        if (installed) adapter3->QueryVideoMemoryInfo(0, DXGI_MEMORY_SEGMENT_GROUP_LOCAL, &info);
    }
    if (adapter3) adapter3->Release();
    if (adapter) adapter->Release();
    factory->Release();
    log::line("video memory hook: %s, local budget cap %llu MiB (0 = off)", installed ? "installed" : "NOT installed",
              local_budget_cap_bytes / kBytesPerMebibyte);
    return installed;
}

}  // namespace cdperf::video_memory_hook
