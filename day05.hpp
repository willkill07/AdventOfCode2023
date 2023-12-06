#include <charconv>
#include <execution>
#include <string_view>

#include <fmt/core.h>
#include <fmt/ranges.h>
#include <range/v3/all.hpp>

#include <exec/inline_scheduler.hpp>
#include <stdexec/execution.hpp>

namespace {

using std::string_view_literals::operator""sv;
namespace rv = ranges::views;

constexpr std::string_view DIGITS{"0123456789"sv};

struct entry {
  entry(long dst, long src, long count) noexcept
      : src{src}, dst{dst}, count{count} {}

  [[nodiscard]] constexpr inline bool in_range(long i) const noexcept {
    return src <= i and i < src + count;
  }
  [[nodiscard]] constexpr inline long map_value(long i) const noexcept {
    return i + (dst - src);
  }

  constexpr auto operator<=>(entry const &rhs) const noexcept = default;

  long src, dst, count;
};

struct map {

  map(std::string_view text) {
    while (text.find('\n') == 0) {
      text.remove_prefix(1);
    }
    text.remove_prefix(text.find('\n') + 1);
    while (not text.empty()) {
      auto fence1 = text.find(' ');
      auto fence2 = text.find(' ', fence1 + 1);
      auto end = text.find('\n');
      if (end == 0) {
        break;
      }
      std::string_view const num1{text.substr(0, fence1)};
      std::string_view const num2{text.substr(fence1 + 1, fence2 - fence1 - 1)};
      std::string_view const num3{text.substr(fence2 + 1, end - fence2 - 1)};
      long dst, src, count;
      std::from_chars(num1.begin(), num1.end(), dst);
      std::from_chars(num2.begin(), num2.end(), src);
      std::from_chars(num3.begin(), num3.end(), count);
      entries.emplace_back(dst, src, count);
      text.remove_prefix(end + 1);
    }
  }

  [[nodiscard]] inline long map_value(long src) const noexcept {
    auto not_in_range = [=](entry const &e) { return not e.in_range(src); };
    auto sat = entries | rv::drop_while(not_in_range);
    if (not sat.empty()) {
      return ranges::begin(sat)->map_value(src);
    } else {
      return src;
    }
  }

  std::vector<entry> entries;
};

auto get_seeds(std::string_view nums) {
  std::vector<long> values;
  long v;
  while (not nums.empty()) {
    auto start = nums.find_first_of(DIGITS);
    if (start == std::string_view::npos) {
      break;
    }
    auto stop = nums.find_first_not_of(DIGITS, start);
    if (stop == std::string_view::npos) {
      stop = nums.size();
    }
    auto const n = nums.substr(start, stop - start);
    std::from_chars(n.begin(), n.end(), v);
    values.push_back(v);
    nums.remove_prefix(stop);
  }
  return values;
}

struct input {
  input(std::string_view data) {
    auto end_of_seeds = data.find("\n\n");
    seeds = get_seeds(data.substr(0, end_of_seeds));
    data.remove_prefix(end_of_seeds + 2);
    while (not data.empty()) {
      if (auto end = data.find("\n\n"); end == std::string_view::npos) {
        mappings.emplace_back(data);
        data.remove_prefix(data.size());
      } else {
        mappings.emplace_back(data.substr(0, end + 1));
        data.remove_prefix(end + 2);
      }
    }
  }

  std::vector<long> seeds;
  std::vector<map> mappings;
};

auto parse([[maybe_unused]] auto scheduler, std::string_view data) {
  return input{data};
}

auto get_min(std::span<long> totals) {
  return std::reduce(std::execution::par_unseq, totals.begin(), totals.end(),
                     std::numeric_limits<long>::max(),
                     [](auto const &a, auto const &b) {
                       return std::min({a, b});
                     });
}

auto part1(auto scheduler, input const &data) {

  std::span seeds{data.seeds};
  std::span mappings{data.mappings};

  auto process = [=](unsigned i, std::span<long> totals) {
    auto id = seeds[i];
    for (auto m : mappings) {
      id = m.map_value(id);
    }
    totals[i] = id;
  };
  auto [value] =
      stdexec::sync_wait(stdexec::just(std::vector<long>(seeds.size(), 0)) |
                         stdexec::let_value([=](std::vector<long> &totals) {
                           return stdexec::transfer_just(scheduler,
                                                         std::span{totals}) |
                                  stdexec::bulk(seeds.size(), process) |
                                  stdexec::transfer(exec::inline_scheduler{}) |
                                  stdexec::then(get_min);
                         }))
          .value();
  return value;
}

auto calculate_path(long i, std::span<long> totals, long start,
                    std::span<map const> mappings) {
  long id = i + start;
  for (auto const &m : mappings) {
    id = m.map_value(id);
  }
  totals[i] = id;
}

template <typename Scheduler>
auto parallel_process(std::vector<long> &totals, long start, long length,
                      std::span<long const> seeds,
                      std::span<map const> mappings, Scheduler scheduler) {
  return stdexec::transfer_just(scheduler, std::span{totals}, start, mappings) |
         stdexec::bulk(length, calculate_path) |
         stdexec::transfer(exec::inline_scheduler{}) | stdexec::then(get_min);
}

template <typename Scheduler>
auto invoke(size_t i, long length, std::span<long const> seeds,
            std::span<map const> mappings, Scheduler scheduler) {
  return stdexec::just(std::vector<long>(length), seeds[2 * i], length, seeds,
                       mappings, scheduler) |
         stdexec::let_value(parallel_process<Scheduler>);
}

template <typename Scheduler>
auto part2(Scheduler scheduler, input const &data,
           [[maybe_unused]] long part1_answer) {

  return 0l;
  std::span seeds{data.seeds};
  std::span mappings{data.mappings};

  size_t const length{seeds.size() / 2};

  auto process = [=](long i, long start, std::span<long> totals) {
    auto id = start + i;
    for (auto m : mappings) {
      id = m.map_value(id);
    }
    totals[i] = id;
  };

  std::vector<long> results;
  for (auto i : rv::closed_iota(0lu, length)) {
    auto start = seeds[2 * i];
    auto count = seeds[2 * i + 1];
    auto [value] =
      stdexec::sync_wait(stdexec::just(std::vector<long>(count, 0)) |
                         stdexec::let_value([=](std::vector<long> &totals) {
                           return stdexec::transfer_just(scheduler, start,
                                                         std::span{totals}) |
                                  stdexec::bulk(count, process) |
                                  stdexec::transfer(exec::inline_scheduler{}) |
                                  stdexec::then([](auto, auto values) {
                                    return get_min(values);
                                  });
                         }))
          .value();
    results.push_back(value);
  }

  return get_min(results);
}

} // namespace
