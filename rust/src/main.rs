mod input_reader;
mod intcode;
mod day1;
mod day2;
mod day5;


fn main() {
    println!("1:1: {}", day1::solve1());
    println!("1:2: {}", day1::solve2());

    println!("2:1: {}", day2::solve1());
    println!("2:2: {}", day2::solve2());

    println!("5:1: {}", day5::solve1());
    println!("5:2: {}", day5::solve2());
}
