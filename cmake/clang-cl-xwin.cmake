set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR AMD64)

set(XWIN_DIR "$ENV{XWIN_DIR}" CACHE PATH "Directory produced by xwin splat")
if(NOT XWIN_DIR)
    message(FATAL_ERROR "Set XWIN_DIR to the output directory of `xwin splat`.")
endif()

set(CMAKE_C_COMPILER clang-cl)
set(CMAKE_CXX_COMPILER clang-cl)
set(CMAKE_LINKER lld-link)
set(CMAKE_RC_COMPILER llvm-rc)
set(CMAKE_MT llvm-mt)
set(CMAKE_AR llvm-lib)

set(CLANG_RESOURCE_DIR "$ENV{CLANG_RESOURCE_DIR}" CACHE PATH "clang resource directory, needed when clang-cl ships without one")

set(XWIN_TARGET_FLAGS
    --target=x86_64-pc-windows-msvc
    -fuse-ld=lld-link
    /imsvc${XWIN_DIR}/crt/include
    /imsvc${XWIN_DIR}/sdk/include/ucrt
    /imsvc${XWIN_DIR}/sdk/include/um
    /imsvc${XWIN_DIR}/sdk/include/shared
    /imsvc${XWIN_DIR}/sdk/include/winrt)
if(CLANG_RESOURCE_DIR)
    list(APPEND XWIN_TARGET_FLAGS "/clang:-resource-dir=${CLANG_RESOURCE_DIR}")
endif()
string(REPLACE ";" " " XWIN_TARGET_FLAGS "${XWIN_TARGET_FLAGS}")
set(CMAKE_C_FLAGS_INIT "${XWIN_TARGET_FLAGS}")
set(CMAKE_CXX_FLAGS_INIT "${XWIN_TARGET_FLAGS}")

set(XWIN_LINK_FLAGS
    /libpath:${XWIN_DIR}/crt/lib/x86_64
    /libpath:${XWIN_DIR}/sdk/lib/um/x86_64
    /libpath:${XWIN_DIR}/sdk/lib/ucrt/x86_64)
string(REPLACE ";" " " XWIN_LINK_FLAGS "${XWIN_LINK_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS_INIT "${XWIN_LINK_FLAGS}")
set(CMAKE_SHARED_LINKER_FLAGS_INIT "${XWIN_LINK_FLAGS}")
set(CMAKE_MODULE_LINKER_FLAGS_INIT "${XWIN_LINK_FLAGS}")

set(CMAKE_TRY_COMPILE_CONFIGURATION Release)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
