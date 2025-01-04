project(clangd-wheel)
cmake_minimum_required(VERSION 3.16)

# Include the "single source of truth" for the clangd version
include(clangd_version.cmake)
string(REPLACE "-" "" CLANGD_VERSION_SHORT "${CLANGD_VERSION}")
string(REPLACE "." ";" CLANGD_VERSION_LIST ${CLANGD_VERSION})
list(GET CLANGD_VERSION_LIST 0 CLANGD_VERSION_MAJOR)

# Define a build rule clangd
set(LLVM_DOWNLOAD_URL "https://github.com/llvm/llvm-project/releases/download/llvmorg-${CLANGD_VERSION}/llvm-project-${CLANGD_VERSION_SHORT}.src.tar.xz")
include(ExternalProject)
ExternalProject_add(build-clangd
  URL "${LLVM_DOWNLOAD_URL}"
  SOURCE_SUBDIR llvm
  SOURCE_DIR ${CMAKE_BINARY_DIR}/llvm-project
  BINARY_DIR ${CMAKE_BINARY_DIR}/llvm
  UPDATE_COMMAND ""
  INSTALL_COMMAND ""
  USES_TERMINAL_DOWNLOAD 1
  USES_TERMINAL_CONFIGURE 1
  USES_TERMINAL_BUILD 1
  CMAKE_ARGS -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DLLVM_ENABLE_ZSTD=OFF -DLLVM_ENABLE_PROJECTS=clang$<SEMICOLON>clang-tools-extra
  BUILD_COMMAND ${CMAKE_COMMAND} --build . --target clangd
)
set(clangd-executable ${CMAKE_BINARY_DIR}/llvm/bin/clangd${CMAKE_EXECUTABLE_SUFFIX})

# Reduce the size of the executable by executing strip if it is present on the system
find_program(STRIP_EXECUTABLE strip)
if(STRIP_EXECUTABLE)
  add_custom_target(
    strip-clangd
    ALL
    COMMAND ${STRIP_EXECUTABLE} ${clangd-executable}
    COMMENT "Stripping clangd executable for size reduction"
  )
  add_dependencies(strip-clangd build-clangd)
endif()

# Define an installation rule that copies the executable to our Python package
install(
  PROGRAMS
    ${clangd-executable}
  DESTINATION clangd/data/bin
)

install(
  DIRECTORY
    ${CMAKE_BINARY_DIR}/llvm/lib/clang/${CLANGD_VERSION_MAJOR}/include
  DESTINATION clangd/data/lib/clang/${CLANGD_VERSION_MAJOR}
)
