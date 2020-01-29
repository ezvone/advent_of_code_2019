use crate::input_reader;
use crate::intcode::IntCode;

struct ThermalEnvironmentSupervisionTerminal {
    code: Vec<i64>,
}

impl ThermalEnvironmentSupervisionTerminal {
    fn new() -> ThermalEnvironmentSupervisionTerminal {
        let input = input_reader::InputSpec::DayNumber(5);
        let code = input_reader::read_numbers_comma_separated(&input);
        ThermalEnvironmentSupervisionTerminal { code }
    }

    fn run(&mut self, test_unit_id: u64) -> u64 {
        let mut ic = IntCode::new(&mut self.code.iter());
        ic.run();
        if ic.requires_input() {
            ic.write_input(&(test_unit_id as i64));
        } else {
            panic!("Expected that an input would be requested");
        }
        let mut last_output = 0;
        while ic.has_output() {
            if last_output != 0 { panic!("Diagnostic failed with value {}", last_output); }
            last_output = ic.read_output();
        }
        if !ic.finished() { panic!("Expected finish, got {:?}", ic.state); }
        last_output as u64
    }
}

pub fn solve1() -> u64 {
    let mut ga = ThermalEnvironmentSupervisionTerminal::new();
    const AIR_CONDITIONER_UNIT_ID : u64 = 1;
    ga.run(AIR_CONDITIONER_UNIT_ID)
}

pub fn solve2() -> u64 {
    let mut ga = ThermalEnvironmentSupervisionTerminal::new();
    const THERMAL_RADIATOR_CONTROLLER_ID : u64 = 5;
    ga.run(THERMAL_RADIATOR_CONTROLLER_ID)
}
