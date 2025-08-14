cmake_minimum_required(VERSION 3.16...3.31)
project(clangd-wheel)

message(STATUS "clangd-wheel version: ${SKBUILD_PROJECT_VERSION}")
string(REGEX MATCH "^([0-9]+)\.([0-9]+)\.([0-9]+)" CLANGD_VERSION
             "${SKBUILD_PROJECT_VERSION}")
set(CLANGD_VERSION_MAJOR ${CMAKE_MATCH_1}
)# https://cmake.org/cmake/help/latest/variable/CMAKE_MATCH_n.html
message(STATUS "clangd version: ${CLANGD_VERSION}")

set(LLVM_DOWNLOAD_URL
    "https://github.com/llvm/llvm-project/archive/refs/tags/llvmorg-${CLANGD_VERSION}.tar.gz"
)

# Setup base cmake arguments
set(LLVM_CMAKE_ARGS
    -DBUILD_SHARED_LIBS=OFF
    -DCLANG_INCLUDE_DOCS=OFF
    -DCLANG_INCLUDE_TESTS=OFF
    -DCMAKE_BUILD_TYPE=Release
    -DLLVM_BUILD_TOOLS=OFF
    -DLLVM_ENABLE_PROJECTS=clang$<SEMICOLON>clang-tools-extra
    -DLLVM_ENABLE_ZSTD=OFF
    -DLLVM_INCLUDE_BENCHMARKS=OFF
    -DLLVM_INCLUDE_EXAMPLES=OFF
    -DLLVM_INCLUDE_TESTS=OFF
    )

if(DEFINED ENV{SCCACHE_ENABLE} AND "$ENV{SCCACHE_ENABLE}" STREQUAL "ON")
  find_program(SCCACHE sccache)
  list(APPEND LLVM_CMAKE_ARGS "-DCMAKE_C_COMPILER_LAUNCHER=${SCCACHE}")
  list(APPEND LLVM_CMAKE_ARGS "-DCMAKE_CXX_COMPILER_LAUNCHER=${SCCACHE}")
  message(STATUS "Using sccache: ${SCCACHE}")
endif()

include(ExternalProject)
ExternalProject_Add(
  build-clangd
  URL "${LLVM_DOWNLOAD_URL}"
  SOURCE_SUBDIR llvm
  SOURCE_DIR ${CMAKE_BINARY_DIR}/llvm-project
  BINARY_DIR ${CMAKE_BINARY_DIR}/llvm
  UPDATE_COMMAND ""
  INSTALL_COMMAND ""
  USES_TERMINAL_DOWNLOAD 1
  USES_TERMINAL_CONFIGURE 1
  USES_TERMINAL_BUILD 1
  DOWNLOAD_EXTRACT_TIMESTAMP TRUE
  CMAKE_ARGS ${LLVM_CMAKE_ARGS}
  BUILD_COMMAND ${CMAKE_COMMAND} --build . --target clangd)

set(config-subfolder "")
if(CMAKE_GENERATOR MATCHES "Visual Studio")
  set(config-subfolder "Release")
endif()
set(clangd-executable
    ${CMAKE_BINARY_DIR}/llvm/${config-subfolder}/bin/clangd${CMAKE_EXECUTABLE_SUFFIX}
)

set(IS_ARM64_WINDOWS FALSE)
string(TOUPPER "$ENV{VSCMD_ARG_HOST_ARCH}" WIN_HOST_ARCH_UPPER)

if((CMAKE_HOST_SYSTEM_NAME STREQUAL "Windows") AND (WIN_HOST_ARCH_UPPER STREQUAL
                                                    "ARM64"))
  set(IS_ARM64_WINDOWS TRUE)
  message(STATUS "Building for ARM64 Windows")
endif()

message(STATUS "System information:")
message(STATUS "CMake version: ${CMAKE_VERSION}")
message(STATUS "Host system name: ${CMAKE_HOST_SYSTEM_NAME}")
message(STATUS "Host Processor name: ${CMAKE_HOST_SYSTEM_PROCESSOR}")
message(STATUS "VSCMD_ARG_HOST_ARCH: $ENV{VSCMD_ARG_HOST_ARCH}")
message(STATUS "is arm64 windows: ${IS_ARM64_WINDOWS}")

# Reduce the size of the executable by executing strip if it is present on the
# system
find_program(STRIP_EXECUTABLE strip)
if(STRIP_EXECUTABLE AND NOT IS_ARM64_WINDOWS)
  message(STATUS "Add stripping operation for clangd executable")
  add_custom_target(
    strip-clangd ALL
    COMMAND ${STRIP_EXECUTABLE} ${clangd-executable}
    COMMENT "Stripping clangd executable for size reduction")
  add_dependencies(strip-clangd build-clangd)
endif()

# Define an installation rule that copies the executable to our Python package
install(PROGRAMS ${clangd-executable} DESTINATION clangd/data/bin)

install(
  DIRECTORY ${CMAKE_BINARY_DIR}/llvm/lib/clang/${CLANGD_VERSION_MAJOR}/include
  DESTINATION clangd/data/lib/clang/${CLANGD_VERSION_MAJOR})
