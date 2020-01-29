use std::collections::HashMap;

#[derive(Debug)]
pub enum IntCodeState {
    Ready,
    Finished,
    AwaitingInput,
    InputReady(Value),
    OutputReady(Value),
}

type Address = u64;
type Value = i64;

type RelativeAddress = i64;

enum Reference {
    Position(Address),
    Immediate(Value),
}

struct InfiniteMemory {
    data: HashMap<Address, Value>,
}

impl InfiniteMemory {
    fn new<'a, T>(memory_data: &'a mut T) -> InfiniteMemory
    where T: Iterator<Item = &'a Value>
    {
        let mut data = HashMap::<Address, Value>::new();
        for (index, value) in memory_data.enumerate() {
            data.insert(index as Address, *value as Value);
        }
        InfiniteMemory {data}
    }

    fn get(&self, index: &Address) -> Value {
        match self.data.get(index) {
            Some(value) => *value,
            None => 0
        }
    }

    fn set(&mut self, index: &Address, value: &Value) {
        self.data.insert(*index, *value);
    }
}

pub struct IntCode {
    data: InfiniteMemory,
    pub state: IntCodeState,
    instruction_pointer: Address,
    relative_base: Address,
}

impl IntCode {
    pub fn new<'a, T>(data: &'a mut T) -> IntCode
    where T: Iterator<Item = &'a Value>
    {
        IntCode {
            data: InfiniteMemory::new(data),
            state: IntCodeState::Ready,
            instruction_pointer: 0,
            relative_base: 0
        }
    }

    pub fn get(&self, index: Address) -> Value {
        self.data.get(&index)
    }

    pub fn set(&mut self, index: Address, value: Value) {
        self.data.set(&index, &value)
    }

    pub fn finished(&self) -> bool {
        match self.state {
            IntCodeState::Finished => true,
            _ => false
        }
    }

    pub fn has_output(&self) -> bool {
        match self.state {
            IntCodeState::OutputReady(_) => true,
            _ => false
        }
    }

    pub fn requires_input(&self) -> bool {
        match self.state {
            IntCodeState::AwaitingInput => true,
            _ => false
        }
    }

    pub fn run(&mut self) {
        loop {
            match self.state {
                IntCodeState::Ready => self.step(),
                IntCodeState::InputReady(_) => self.step(),
                _ => return
            };
        }
    }

    pub fn read_output(&mut self) -> Value {
        let rtn = match self.state {
            IntCodeState::OutputReady(value) => value,
            _ => panic!("Cannot read_output in current state")
        };
        self.state = IntCodeState::Ready;
        self.run();
        rtn
    }

    pub fn write_input(&mut self, value: &Value) {
        match self.state {
            IntCodeState::AwaitingInput => {
                self.state = IntCodeState::InputReady(*value);
                self.run();
            },
            _ => panic!("Cannot write_input in current state")
        };
    }

    fn get_reference(&self, index: u32) -> Reference
    {
        let instruction_value = self.data.get(&self.instruction_pointer) as u64;
        let mode_digits = instruction_value / 100;
        match mode_digits / 10u64.pow(index-1) % 10 {
            0 => {
                let val = self.data.get(&(self.instruction_pointer + index as Address));
                Reference::Position(val as Address)
            },
            1 => {
                let val = self.data.get(&(self.instruction_pointer + index as Address));
                Reference::Immediate(val)
            },
            2 => {
                let val = self.data.get(&(self.instruction_pointer + index as Address));
                let addr = self.relative_base as RelativeAddress + val;
                Reference::Position(addr as Address)
            },
            _ => panic!("Unexpexted address mode"),
        }
    }

    fn read(&self, index: u32) -> Value {
        match self.get_reference(index) {
            Reference::Position(addr) => self.data.get(&addr),
            Reference::Immediate(val) => val,
        }
    }

    fn write (&mut self, index: u32, value: &Value) {
        let address = match self.get_reference(index) {
            Reference::Position(addr) => addr,
            Reference::Immediate(_) => panic!("Cannot write in immediate mode"),
        };
        self.data.set(&address, value);
    }

    fn step(&mut self) {

        #[derive(Debug)]
        enum Instruction {
            Addition,
            Multiplication,
            Input,
            Output,
            JumpIf,
            JumpUnless,
            IsLess,
            IsEqual,
            UpdateRelativeBase,
            Exit,
        }

        let instruction_value = self.data.get(&self.instruction_pointer) as u64;
        let instr = match instruction_value % 100 {
            1 => Instruction::Addition,
            2 => Instruction::Multiplication,
            3 => Instruction::Input,
            4 => Instruction::Output,
            5 => Instruction::JumpIf,
            6 => Instruction::JumpUnless,
            7 => Instruction::IsLess,
            8 => Instruction::IsEqual,
            9 => Instruction::UpdateRelativeBase,
            99 => Instruction::Exit,
            _ => panic!("Unknown instr code"),
        };

        self.instruction_pointer = match self.state {
            IntCodeState::InputReady(value) => {
                match instr {
                    Instruction::Input => {
                        self.write(1, &value);
                        self.state = IntCodeState::Ready;
                        self.instruction_pointer + 2
                    },
                    _ => panic!("Unexpected InputReady when instr is not Input ({:?})", instr),
                }
            },
            IntCodeState::Ready => {
                match instr {
                    Instruction::Addition => {
                        self.write(3, &(self.read(1) + self.read(2)));
                        self.instruction_pointer + 4
                    },
                    Instruction::Multiplication => {
                        self.write(3, &(self.read(1) * self.read(2)));
                        self.instruction_pointer + 4
                    },
                    Instruction::Input => {
                        self.state = IntCodeState::AwaitingInput;
                        self.instruction_pointer
                    },
                    Instruction::Output => {
                        self.state = IntCodeState::OutputReady(self.read(1));
                        self.instruction_pointer + 2
                    },
                    Instruction::JumpIf => {
                        if self.read(1) != 0 {
                            self.read(2) as Address
                        } else {
                            self.instruction_pointer + 3
                        }
                    },
                    Instruction::JumpUnless => {
                        if self.read(1) == 0 {
                            self.read(2) as Address
                        } else {
                            self.instruction_pointer + 3
                        }
                    },
                    Instruction::IsLess => {
                        if self.read(1) < self.read(2) {
                            self.write(3, &1)
                        } else {
                            self.write(3, &0)
                        }
                        self.instruction_pointer + 4
                    },
                    Instruction::IsEqual => {
                        if self.read(1) == self.read(2) {
                            self.write(3, &1)
                        } else {
                            self.write(3, &0)
                        }
                        self.instruction_pointer + 4
                    },
                    Instruction::UpdateRelativeBase => {
                        let tmp = (self.relative_base as RelativeAddress) + self.read(1);
                        self.relative_base = tmp as Address;
                        self.instruction_pointer + 2
                    },
                    Instruction::Exit => {
                        self.state = IntCodeState::Finished;
                        self.instruction_pointer
                    }
                }
            },
            _ => panic!("Cannot step in current state")
        }
    }
}
