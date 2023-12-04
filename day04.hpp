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

constexpr std::string_view DIGITS{"0123456789"sv};

auto read_numbers(std::string_view nums) {
  std::vector<int> values;
  int v;
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
  std::sort(values.begin(), values.end());
  return values;
}

struct card {
  std::vector<int> winners;
  std::vector<int> all;
  card(std::string_view line) {
    line.remove_prefix(line.find_first_of(':'));
    size_t const sep = line.find_first_of('|');
    winners = read_numbers(line.substr(0, sep));
    all = read_numbers(line.substr(sep + 1));
  }
};

auto parse([[maybe_unused]] auto scheduler, std::string_view input) {
  std::vector<card> cards;
  while (not input.empty()) {
    auto split = input.find_first_of('\n');
    if (split == std::string_view::npos) {
      break;
    }
    auto line = input.substr(0, split);
    if (line.empty()) {
      break;
    }
    cards.emplace_back(line);
    input.remove_prefix(split + 1);
  }
  return cards;
}

auto part1(auto scheduler, std::vector<card> const &cards) {
  std::span games{cards};
  auto process = [=](unsigned i, std::span<int> totals) {
    auto &[winners, all] = games[i];
    auto set = ranges::views::set_intersection(all, winners);
    auto const count{ranges::distance(set.begin(), set.end())};
    if (count > 0) {
      totals[i] = (1 << (count - 1));
    }
  };
  auto [value] =
      stdexec::sync_wait(
          stdexec::just(std::vector<int>(games.size(), 0)) |
          stdexec::let_value([=](std::vector<int> &totals) {
            return stdexec::transfer_just(scheduler, std::span{totals}) |
                   stdexec::bulk(games.size(), process) |
                   stdexec::transfer(exec::inline_scheduler{}) |
                   stdexec::then([=](std::span<int> totals) {
                     return std::reduce(std::execution::par_unseq,
                                        totals.begin(), totals.end());
                   });
          }))
          .value();
  return value;
}

auto part2(auto scheduler, std::vector<card> const &cards,
           [[maybe_unused]] int part1_answer) {
  std::span games{cards};
  auto process = [=](unsigned i, std::span<int> totals, std::span<int> counts) {
    auto &[winners, all] = games[i];
    auto set = ranges::views::set_intersection(all, winners);
    totals[i] = ranges::distance(set.begin(), set.end());
    counts[i] = 1;
  };
  auto [value] =
      stdexec::sync_wait(
          stdexec::just(std::vector<int>(games.size(), 0),
                        std::vector<int>(games.size(), 0)) |
          stdexec::let_value(
              [=](std::vector<int> &totals, std::vector<int> &counts) {
                return stdexec::transfer_just(scheduler, std::span{totals},
                                              std::span{counts}) |
                       stdexec::bulk(games.size(), process) |
                       stdexec::transfer(exec::inline_scheduler{}) |
                       stdexec::then([=](std::span<int> totals,
                                         std::span<int> counts) {
                         for (auto [i, v] : ranges::views::enumerate(totals)) {
                           for (unsigned long j{i + 1}; j <= i + v; ++j) {
                             counts[j] += counts[i];
                           }
                         }
                         return std::reduce(std::execution::par_unseq,
                                            counts.begin(), counts.end(), 0);
                       });
              }))
          .value();
  return value;
}

} // namespace
