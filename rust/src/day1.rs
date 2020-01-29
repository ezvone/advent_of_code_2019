use crate::input_reader;


fn get_required_fuel(mass: u64) -> u64 {
    mass / 3 - 2
}

fn get_required_fuel_recursive(mass: u64) -> u64 {
    if mass / 3 > 2 {
        let fuel = mass / 3 - 2;
        fuel + get_required_fuel_recursive(fuel)
    } else {
        0
    }
}

pub fn solve1() -> u64 {
    let mut total: u64 = 0;
    let input = input_reader::InputSpec::DayNumber(1);
    for mass in input_reader::read_number_per_line(&input) {
        total += get_required_fuel(mass)
    }
    total
}

pub fn solve2() -> u64 {
    let mut total: u64 = 0;
    let input = input_reader::InputSpec::DayNumber(1);
    for mass in input_reader::read_number_per_line(&input) {
        total += get_required_fuel_recursive(mass)
    }
    total
}
