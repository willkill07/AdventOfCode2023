#include <fstream>
#include <iterator>
#include <string_view>

#include <fmt/core.h>

#include <exec/static_thread_pool.hpp>
#if ENABLE_GPU
#include <nvexec/stream_context.cuh>
#endif

#if ENABLE_GPU
#define DECLARE_DAY(DAY_FN)                                                    \
  template<typename Executor>                                                  \
  void DAY_FN(Executor&, std::string_view const);                              \
  extern template void DAY_FN<exec::static_thread_pool>(                       \
    exec::static_thread_pool&,                                                 \
    std::string_view const);                                                   \
  extern template void DAY_FN<nvexec::stream_context>(nvexec::stream_context&, \
                                                      std::string_view const);
#else
#define DECLARE_DAY(DAY_FN)                                                    \
  template<typename Executor>                                                  \
  void DAY_FN(Executor&, std::string_view const);                              \
  extern template void DAY_FN<exec::static_thread_pool>(                       \
    exec::static_thread_pool&,                                                 \
    std::string_view const);
#endif

DECLARE_DAY(day01)
DECLARE_DAY(day02)
DECLARE_DAY(day03)
DECLARE_DAY(day04)

template<size_t N>
std::string
file_contents(const char (&filename)[N])
{
  std::ifstream ifs{ filename };
  return { std::istreambuf_iterator{ ifs }, {} };
}

void
run_all(auto& executor)
{
  day01(executor, file_contents("inputs/day01.txt"));
  day02(executor, file_contents("inputs/day02.txt"));
  day03(executor, file_contents("inputs/day03.txt"));
  day04(executor, file_contents("inputs/day04.txt"));
}

int
main()
{
  fmt::print("CPU Execution:\n");
  exec::static_thread_pool cpu_executor{ std::thread::hardware_concurrency() };
  run_all(cpu_executor);
#if ENABLE_GPU
  fmt::print("GPU Execution:\n");
  nvexec::stream_context gpu_executor{};
  run_all(gpu_executor);
#endif
}
