use crate::input_reader;
use crate::intcode::IntCode;

struct GravityAssist {
    code: Vec<i64>,
}

impl GravityAssist {
    fn new() -> GravityAssist {
        let input = input_reader::InputSpec::DayNumber(2);
        let code = input_reader::read_numbers_comma_separated(&input);
        GravityAssist { code }
    }
    fn run(&mut self, noun: u64, verb: u64) -> u64 {
        let mut ic = IntCode::new(&mut self.code.iter());
        ic.set(1, noun as i64);
        ic.set(2, verb as i64);
        ic.run();
        ic.get(0) as u64
    }
}

pub fn solve1() -> u64 {
    let mut ga = GravityAssist::new();
    ga.run(12, 2)
}

pub fn solve2() -> u64 {
    let mut ga = GravityAssist::new();
    for noun in 0..100 {
        for verb in 0..100 {
            match ga.run(noun, verb) {
                19690720 => return 100 * noun + verb,
                _ => (),
            }
        }
    }
    panic!("No result found")
}
