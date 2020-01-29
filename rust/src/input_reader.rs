use std::string::String;
use std::path::Path;
use std::env;
use std::fs;
use std::str::FromStr;
use std::fmt::Debug;


#[allow(dead_code)]
pub enum InputSpec {
    FilePath(String),
    DayNumber(u8),
    DirectInput(String)
}

fn get_day_path(day: &u8) -> String {
    let args: Vec<_> = env::args().collect();
    let data_dir = Path::new(&args[0]).join("../../../../data");
    String::from(data_dir.join(format!("day{}input.txt", day)).as_path().to_str().unwrap())
}

fn read_input(input: &InputSpec) -> String
{
    match input {
        InputSpec::FilePath(p) => fs::read_to_string(p).unwrap(),
        InputSpec::DayNumber(n) => fs::read_to_string(get_day_path(n)).unwrap(),
        InputSpec::DirectInput(s) => s.clone()
    }
}

#[allow(dead_code)]
pub fn read_lines(input: &InputSpec) -> Vec<String>
{
    let mut rtn = Vec::new();
    for line in read_input(input).split('\n') {
        rtn.push(String::from(line));
    }
    rtn
}

pub fn read_number_per_line<T>(input: &InputSpec) -> Vec<T>
where T: FromStr, <T as FromStr>::Err: Debug
{
    let mut rtn = Vec::new();
    for line in read_input(input).split('\n') {
        if line.len() > 0 {
            rtn.push(line.parse::<T>().unwrap());
        }
    }
    rtn
}

pub fn read_numbers_comma_separated<T>(input: &InputSpec) -> Vec<T>
where T: FromStr, <T as FromStr>::Err: Debug
{
    let mut rtn = Vec::new();
    for value in read_input(input).split(',') {
        let value = value.trim();
        if value.len() > 0 {
            rtn.push(value.parse::<T>().unwrap());
        }
    }
    rtn
}