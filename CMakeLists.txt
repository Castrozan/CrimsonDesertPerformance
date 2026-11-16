cmake_minimum_required(VERSION 3.24)
project(CrimsonDesertPerformance VERSION 0.1.0 LANGUAGES CXX)

if(NOT MSVC OR NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
    message(FATAL_ERROR "Build for x64 Windows with clang-cl or MSVC; see scripts/build-linux.sh.")
endif()

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

add_compile_definitions(WIN32_LEAN_AND_MEAN NOMINMAX UNICODE _UNICODE _WIN32_WINNT=0x0A00
                        CDPERF_VERSION="${PROJECT_VERSION}")
add_compile_options(/permissive- /utf-8 /EHsc /W4)

add_library(cdperf SHARED
    src/dllmain.cpp
    src/log.cpp
    src/settings.cpp
    src/video_memory_hook.cpp
)
target_include_directories(cdperf PRIVATE src)
target_link_libraries(cdperf PRIVATE dxgi)
set_target_properties(cdperf PROPERTIES OUTPUT_NAME cdperf SUFFIX ".asi")
