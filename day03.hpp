#include <charconv>
#include <execution>
#include <numeric>
#include <string_view>

#include <fmt/core.h>
#include <range/v3/all.hpp>

#include <exec/inline_scheduler.hpp>
#include <stdexec/execution.hpp>

namespace {

using std::string_view_literals::operator""sv;

struct symbol {
  int row;
  int col;
  bool is_gear;
  inline symbol(int r, int c, char v) noexcept
      : row{r}, col{c}, is_gear{v == '*'} {}
};

struct number {
  int row;
  int col;
  int value;
  int width;

  inline number(int r, int c, std::string_view n) noexcept
      : row{r}, col{c}, width{static_cast<int>(n.size())} {
    std::from_chars(n.data(), n.data() + n.size(), value);
  }
};

struct state {
  std::vector<number> numbers;
  std::vector<symbol> symbols;
};

constexpr bool adjacent(number const &n, symbol const &s) noexcept {
  return (n.row - 1 <= s.row and s.row <= n.row + 1) and
         (n.col - 1 <= s.col and s.col <= n.col + n.width);
}

auto parse([[maybe_unused]] auto scheduler, std::string_view input) {
  state s;
  int row{0}, col{0};
  while (not input.empty()) {
    auto const skip = input.find_first_not_of('.');
    col += skip;
    input.remove_prefix(skip);
    if (input.empty()) {
      break;
    }
    if ('0' <= input[0] and input[0] <= '9') {
      // digit
      auto len = input.find_first_not_of("0123456789"sv);
      s.numbers.emplace_back(row, col, input.substr(0, len));
      col += len;
      input.remove_prefix(len);
    } else if (input[0] == '\n') {
      // newline
      ++row;
      col = 0;
      input.remove_prefix(1);
    } else {
      // symbol
      s.symbols.emplace_back(row, col, input[0]);
      ++col;
      input.remove_prefix(1);
    }
  }
  return s;
}

auto part1(auto scheduler, state const &s) {
  std::span numbers{s.numbers};
  std::span symbols{s.symbols};
  auto process = [=](unsigned i, std::span<int> totals) {
    auto const &num = numbers[i];
    auto next_to = [&](symbol const &s) { return adjacent(num, s); };
    if (ranges::any_of(symbols, next_to)) {
      totals[i] = num.value;
    }
  };
  auto [value] =
      stdexec::sync_wait(
          stdexec::just(std::vector<int>(numbers.size(), 0)) |
          stdexec::let_value([=](std::vector<int> &totals) {
            return stdexec::transfer_just(scheduler, std::span{totals}) |
                   stdexec::bulk(numbers.size(), process) |
                   stdexec::transfer(exec::inline_scheduler{}) |
                   stdexec::then([=](std::span<int> totals) {
                     return std::reduce(std::execution::par_unseq,
                                        totals.begin(), totals.end());
                   });
          }))
          .value();
  return value;
}

auto part2(auto scheduler, state const &s, [[maybe_unused]] int part1_answer) {
  std::span numbers{s.numbers};
  std::span symbols{s.symbols};
  auto process = [=](unsigned i, std::span<int> totals) {
    auto const &sym = symbols[i];
    if (not sym.is_gear) {
      return;
    }
    int product{1}, count{0};
    auto next_to = [&](number const &n) { return adjacent(n, sym); };
    for (number const& n: numbers | ranges::views::filter(next_to)) {
      product *= n.value;
      ++count;
    }
    if (count == 2) {
      totals[i] = product;
    }
  };
  auto [value] =
      stdexec::sync_wait(
          stdexec::just(std::vector<int>(symbols.size(), 0)) |
          stdexec::let_value([=](std::vector<int> &totals) {
            return stdexec::transfer_just(scheduler, std::span{totals}) |
                   stdexec::bulk(symbols.size(), process) |
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
