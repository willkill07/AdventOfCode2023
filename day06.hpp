#include <charconv>
#include <execution>
#include <string_view>

#include <range/v3/all.hpp>

#include <exec/inline_scheduler.hpp>
#include <stdexec/execution.hpp>

namespace {

using std::string_view_literals::operator""sv;

constexpr std::string_view DIGITS{"0123456789"sv};

auto read_numbers(std::string_view nums) {
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

struct info {
  std::vector<long> time;
  std::vector<long> distance;
};

auto parse([[maybe_unused]] auto scheduler, std::string_view input) {
  info result;
  auto split = input.find_first_of('\n');
  result.time = read_numbers(input.substr(0, split));
  result.distance = read_numbers(input.substr(split + 2));
  return result;
}

auto part1(auto scheduler, info const &input) {
  std::span time{input.time};
  std::span distance{input.distance};
  auto process = [=](unsigned i, std::span<long> totals) {
    auto t = time[i];
    auto d = distance[i];
    double const mid = t / 2.0;
    double const disc = std::sqrt(t * t / 4 - d);
    totals[i] =
        static_cast<long>(1 + std::floor(mid + disc) - std::ceil(mid - disc));
  };
  auto [value] =
      stdexec::sync_wait(
          stdexec::just(std::vector<long>(time.size(), 0)) |
          stdexec::let_value([=](std::vector<long> &totals) {
            return stdexec::transfer_just(scheduler, std::span{totals}) |
                   stdexec::bulk(time.size(), process) |
                   stdexec::transfer(exec::inline_scheduler{}) |
                   stdexec::then([=](std::span<long> totals) {
                     return std::reduce(std::execution::par_unseq,
                                        totals.begin(), totals.end(), 1,
                                        std::multiplies<>{});
                   });
          }))
          .value();
  return value;
}

auto part2([[maybe_unused]] auto scheduler, info const &input,
           [[maybe_unused]] int part1_answer) {
  std::stringstream ss;
  long t, d;
  ranges::copy(input.time, std::ostream_iterator<long>(ss));
  ss << ' ';
  ranges::copy(input.distance, std::ostream_iterator<long>(ss));
  ss >> t >> d;
  double const mid = t / 2.0;
  double const disc = std::sqrt(t * t / 4 - d);
  return static_cast<long>(1 + std::floor(mid + disc) - std::ceil(mid - disc));
}

} // namespace
