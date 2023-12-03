#include <charconv>
#include <execution>
#include <numeric>
#include <string_view>

#include <fmt/core.h>
#include <range/v3/all.hpp>
#include <stdexec/execution.hpp>

namespace {

using std::string_view_literals::operator""sv;

constexpr std::string_view DIGITS{"01234567789"};

struct trial {
  int red{0};
  int green{0};
  int blue{0};

  trial() = default;

  trial(std::string_view data) {

    auto get = [&](char c) -> int & {
      if (c == 'r') {
        return red;
      } else if (c == 'g') {
        return green;
      } else {
        return blue;
      }
    };

    size_t const n1 = data.find_first_of(DIGITS);
    size_t const e1 = data.find_first_not_of(DIGITS, n1);
    std::string_view const num1{data.substr(n1, e1 - n1)};
    std::from_chars(num1.data(), num1.data() + num1.size(), get(data[e1 + 1]));

    size_t const n2 = data.find_first_of(DIGITS, e1 + 1);
    if (n2 == std::string::npos) {
      return;
    }
    size_t const e2 = data.find_first_not_of(DIGITS, n2);
    std::string_view const num2{data.substr(n2, e2 - n2)};
    std::from_chars(num2.data(), num2.data() + num2.size(), get(data[e2 + 1]));

    size_t const n3 = data.find_first_of(DIGITS, e2 + 1);
    if (n3 == std::string::npos) {
      return;
    }
    size_t const e3 = data.find_first_not_of(DIGITS, n3);
    std::string_view const num3{data.substr(n3, e3 - n3)};
    std::from_chars(num3.data(), num3.data() + num3.size(), get(data[e3 + 1]));
  }
};

struct game {
  int id{0};
  std::vector<trial> rounds{};

  game(std::string_view line) {
    auto num_begin = line.find_first_of(DIGITS);
    auto num_end = line.substr(num_begin).find_first_not_of(DIGITS);
    std::string_view num{line.substr(num_begin, num_end)};
    std::from_chars(num.data(), num.data() + num.size(), id);
    line = line.substr(num_begin + num_end + 1);
    while (not line.empty()) {
      auto delim = line.find_first_of(";\n");
      auto round = line;
      if (delim != std::string_view::npos) {
        round = line.substr(0, delim);
        line = line.substr(delim + 1);
      } else {
        line = line.substr(line.size());
      }
      rounds.emplace_back(round);
    }
  }
};

auto parse([[maybe_unused]] auto scheduler, std::string_view input) {
  std::vector<game> output;
  while (not input.empty()) {
    auto const end = input.find_first_of('\n');
    if (end == std::string_view::npos) {
      break;
    }
    auto const line = input.substr(0, end);
    if (not line.empty()) {
      output.emplace_back(line);
    }
    input.remove_prefix(end + 1);
  }
  return output;
}

auto part1(auto scheduler, std::vector<game> const &parsed) {
  std::span lines{parsed};
  auto process = [=](unsigned i, std::span<int> totals) {
    auto &gm = lines[i];
    if (ranges::all_of(gm.rounds, [](trial const &t) {
          return t.red <= 12 && t.green <= 13 && t.blue <= 14;
        })) {
      totals[i] = gm.id;
    }
  };
  auto [value] =
      stdexec::sync_wait(
          stdexec::just(std::vector<int>(lines.size(), 0)) |
          stdexec::let_value([=](std::vector<int> &totals) {
            return stdexec::transfer_just(scheduler, std::span{totals}) |
                   stdexec::bulk(lines.size(), process) |
                   stdexec::then([=](std::span<int> totals) {
                     return std::reduce(std::execution::par_unseq,
                                        totals.begin(), totals.end());
                   });
          }))
          .value();
  return value;
}

auto part2(auto scheduler, std::vector<game> const &parsed,
           [[maybe_unused]] int part1_answer) {
  std::span lines{parsed};
  auto process = [=](unsigned i, std::span<int> totals) {
    auto &gm = lines[i];
    auto [r, g, b] = std::reduce(gm.rounds.begin(), gm.rounds.end(), trial{},
                                 [](trial t1, trial const &t2) {
                                   t1.red = std::max(t1.red, t2.red);
                                   t1.green = std::max(t1.green, t2.green);
                                   t1.blue = std::max(t1.blue, t2.blue);
                                   return t1;
                                 });
    totals[i] = r * g * b;
  };

  auto [value] =
      stdexec::sync_wait(
          stdexec::just(std::vector<int>(lines.size(), 0)) |
          stdexec::let_value([=](std::vector<int> &totals) {
            return stdexec::transfer_just(scheduler, std::span{totals}) |
                   stdexec::bulk(lines.size(), process) |
                   stdexec::then([=](std::span<int> totals) {
                     return std::reduce(std::execution::par_unseq,
                                        totals.begin(), totals.end());
                   });
          }))
          .value();
  return value;
}

} // namespace
