cmake_minimum_required(VERSION 3.26)
project(ParallelProjects CXX)

option(USE_GPU Off)

# Set newest C++ standard globally
set(CXX_STANDARD 23)
set(CXX_EXTENSIONS On)

if(NOT CMAKE_CXX_COMPILER_ID STREQUAL NVHPC)
  set(CMAKE_CXX_FLAGS_DEBUG "-g -ggdb")
  set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-Og -g")
  set(CMAKE_CXX_FLAGS_MINSIZEREL "-Os")
  set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native")
endif()

if(NOT CMAKE_BUILD_TYPE)
  message(STATUS "Setting build type to 'RelWithDebInfo' as none was specified.")
  set(CMAKE_BUILD_TYPE RelWithDebInfo CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

find_program(CCACHE_FOUND "ccache")
if(CCACHE_FOUND)
  set(CMAKE_C_COMPILER_LAUNCHER ccache)
  set(CMAKE_CXX_COMPILER_LAUNCHER ccache)
endif()

include(cmake/CPM.cmake)

CPMAddPackage("gh:doctest/doctest#v2.4.11")
CPMAddPackage("gh:fmtlib/fmt#10.1.1")
CPMAddPackage("gh:tartanllama/expected#v1.1.0")
CPMAddPackage("gh:tartanllama/optional#v1.1.0")

CPMAddPackage(
  NAME range-v3
  GITHUB_REPOSITORY ericniebler/range-v3
  GIT_TAG 0.12.0
  OPTIONS "RANGE_V3_EXAMPLES Off" "RANGE_V3_TESTS Off"
  SYSTEM
)

CPMAddPackage(
  NAME stdexec
  GITHUB_REPOSITORY NVIDIA/stdexec
  GIT_TAG main
  OPTIONS "STDEXEC_BUILD_EXAMPLES Off" "STDEXEC_BUILD_TESTS Off"
  SYSTEM
)

if(USE_GPU)
  if(CMAKE_CXX_COMPILER_ID STREQUAL NVHPC)
    set(ENABLE_GPU 1)
  else()
    include(CheckLanguage)
    check_language(CUDA)
    if(CMAKE_CUDA_COMPILER)
      set(ENABLE_GPU 1)
      enable_language(CUDA)
    else()
      set(ENABLE_GPU 0)
    endif()
  endif()
else()
  set(ENABLE_GPU 0)
endif()

add_library(advent_common INTERFACE)
target_compile_options(advent_common INTERFACE 
  $<$<COMPILE_LANG_AND_ID:CXX,GCC,Clang>:-Wall -Wextra -Wpedantic -Wconversion -Wno-deprecated-builtins>
  $<$<COMPILE_LANG_AND_ID:CXX,Clang>:-stdlib=libstdc++>
)
target_link_libraries(advent_common INTERFACE
  tl::expected
  tl::optional
  fmt::fmt
  range-v3
  STDEXEC::stdexec
  doctest::doctest
)

add_library(advent_cpu)
target_include_directories(advent_cpu PUBLIC ${CMAKE_SOURCE_DIR})
target_compile_definitions(advent_cpu PRIVATE USE_GPU=0)
target_compile_options(advent_cpu PRIVATE $<$<COMPILE_LANG_AND_ID:CXX,NVHPC>:-stdpar=multicore --experimental-stdpar>)
if(NOT CMAKE_CXX_COMPILER_ID STREQUAL NVHPC)
  find_package(TBB REQUIRED)
  target_link_libraries(advent_cpu PUBLIC tbb)
endif()
target_link_libraries(advent_cpu PUBLIC advent_common)

if(ENABLE_GPU)
  add_library(advent_gpu)
  target_include_directories(advent_gpu PUBLIC ${CMAKE_SOURCE_DIR})
  target_compile_definitions(advent_gpu PRIVATE USE_GPU=1)
  target_link_libraries(advent_gpu PUBLIC advent_common)
  if(CMAKE_CXX_COMPILER_ID STREQUAL NVHPC)
    target_compile_options(advent_gpu PUBLIC -stdpar=gpu -gpu=managed)
    target_link_options(advent_gpu PUBLIC -stdpar=gpu -gpu=managed)
  else()
    set_target_properties(advent_gpu PROPERTIES CUDA_ARCHITECTURES "89")
  endif()
endif()

function(add_day ADVENT_DAY)
  set(day_file ${CMAKE_SOURCE_DIR}/gen/cpu/${ADVENT_DAY}.cpp)
  configure_file(template/Day.cpp.in ${day_file} @ONLY)
  target_sources(advent_cpu PRIVATE ${day_file})
  if(ENABLE_GPU)
    set(day_file ${CMAKE_SOURCE_DIR}/gen/gpu/${ADVENT_DAY}.cpp)
    configure_file(template/Day.cpp.in ${day_file} @ONLY)
    target_sources(advent_gpu PRIVATE ${day_file})
    if(NOT CMAKE_CXX_COMPILER_ID STREQUAL NVHPC)
      set_source_files_properties(${day_file} PROPERTIES LANGUAGE CUDA)
    endif()
  endif()
endfunction()

add_executable(AdventOfCode2023)
target_sources(AdventOfCode2023 PRIVATE advent.cpp)
target_compile_definitions(AdventOfCode2023 PRIVATE -DENABLE_GPU=${ENABLE_GPU})
target_link_libraries(AdventOfCode2023 PUBLIC advent_cpu)
if(ENABLE_GPU)
  target_link_libraries(AdventOfCode2023 PUBLIC advent_gpu)
endif()

add_day(day01)
add_day(day02)
add_day(day03)
add_day(day04)
