#include <execution>
#include <numeric>
#include <string_view>

#include <fmt/core.h>
#include <range/v3/all.hpp>
#include <tl/optional.hpp>

#include <exec/inline_scheduler.hpp>
#include <stdexec/execution.hpp>

namespace {

using std::string_view_literals::operator""sv;

namespace rv = ranges::views;

auto parse([[maybe_unused]] auto scheduler, std::string_view input) {
  std::vector<std::string_view> lines;
  lines.reserve(1000);
  while (not input.empty()) {
    auto const end = input.find_first_of('\n');
    if (end == std::string_view::npos) {
      break;
    }
    auto const line = input.substr(0, end);
    if (not line.empty()) {
      lines.push_back(line);
    }
    input.remove_prefix(end + 1);
  }
  return lines;
}

auto part1(auto scheduler, std::vector<std::string_view> const &parsed) {
  std::span lines{parsed};
  auto calculate_score = [=](unsigned i, std::span<int> totals) {
    auto const line = lines[i];
    auto is_digit = [](auto c) { return '0' <= c && c <= '9'; };
    auto first = ranges::find_if(line, is_digit);
    auto last = std::prev(ranges::find_if(line | rv::reverse, is_digit).base());
    int const lo{*first - '0'};
    int const hi{*last - '0'};
    totals[i] = (lo * 10 + hi);
  };
  auto [value] =
      stdexec::sync_wait(
          stdexec::just(std::vector<int>(lines.size(), 0)) |
          stdexec::let_value([=](std::vector<int> &totals) {
            return stdexec::transfer_just(scheduler, std::span{totals}) |
                   stdexec::bulk(lines.size(), calculate_score) |
                   stdexec::transfer(exec::inline_scheduler{}) |
                   stdexec::then([=](std::span<int> totals) {
                     return std::reduce(std::execution::par_unseq,
                                        totals.begin(), totals.end());
                   });
          }))
          .value();
  return value;
}

auto part2(auto scheduler, std::vector<std::string_view> const &parsed,
           [[maybe_unused]] int part1_answer) {
  std::span lines{parsed};
  auto calculate_score = [=](unsigned i, std::span<int> totals) {
    auto line = lines[i];
    auto is_digit = [](auto c) { return '0' <= c && c <= '9'; };
    auto first = ranges::find_if(line, is_digit);
    auto last = std::prev(ranges::find_if(line | rv::reverse, is_digit).base());
    int lo{*first - '0'};
    int hi{*last - '0'};
    std::string_view const front{line.begin(), first};
    std::string_view const back{std::next(last), line.end()};
    constexpr std::array values{"one"sv,   "two"sv,   "three"sv,
                                "four"sv,  "five"sv,  "six"sv,
                                "seven"sv, "eight"sv, "nine"sv};
    for (tl::optional<size_t> index; auto [i, v] : rv::enumerate(values)) {
      if (auto it = ranges::search(front, v); not it.empty()) {
        if (auto offset = std::distance(back.begin(), it.begin());
            not index.has_value() or offset < *index) {
          index = offset;
          lo = i + 1;
        }
      }
    }
    for (tl::optional<size_t> index; auto [i, v] : rv::enumerate(values)) {
      if (auto it = ranges::search(back, v); not it.empty()) {
        if (auto offset = std::distance(back.begin(), it.begin());
            not index.has_value() or offset > *index) {
          index = offset;
          hi = i + 1;
        }
      }
    }
    totals[i] = (lo * 10 + hi);
  };
  auto [value] =
      stdexec::sync_wait(
          stdexec::just(std::vector<int>(lines.size(), 0)) |
          stdexec::let_value([=](std::vector<int> &totals) {
            return stdexec::transfer_just(scheduler, std::span{totals}) |
                   stdexec::bulk(lines.size(), calculate_score) |
                   stdexec::transfer(exec::inline_scheduler{}) |
                   stdexec::then([=](std::span<int> totals) {
                     return std::reduce(std::execution::par_unseq,
                                        totals.begin(), totals.end());
                   });
          }))
          .value();
  return value;
}

} // namespace
