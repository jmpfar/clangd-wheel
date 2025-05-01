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
  CMAKE_ARGS -DCMAKE_BUILD_TYPE=Release
             -DBUILD_SHARED_LIBS=OFF
             -DLLVM_ENABLE_ZSTD=OFF
             -DLLVM_INCLUDE_TESTS=OFF
             -DLLVM_INCLUDE_EXAMPLES=OFF
             -DLLVM_INCLUDE_BENCHMARKS=OFF
             -DLLVM_BUILD_TOOLS=OFF
             -DCLANG_INCLUDE_TESTS=OFF
             -DCLANG_INCLUDE_DOCS=OFF
             -DLLVM_ENABLE_PROJECTS=clang-tools-extra
  BUILD_COMMAND ${CMAKE_COMMAND} --build . --target clangd)

set(config-subfolder "")
if(CMAKE_GENERATOR MATCHES "Visual Studio")
  set(config-subfolder "Release")
endif()
set(clangd-executable
    ${CMAKE_BINARY_DIR}/llvm/${config-subfolder}/bin/clangd${CMAKE_EXECUTABLE_SUFFIX}
)

# Reduce the size of the executable by executing strip if it is present on the
# system
find_program(STRIP_EXECUTABLE strip)
if(STRIP_EXECUTABLE)
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
