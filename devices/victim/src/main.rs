use device_types::Device;
use std::env;
use std::time::Duration;
use std::thread::sleep;

struct Target {}

impl Device for Target {}
impl Target {
    pub fn new() -> Target {
        Target {}
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();

    let host = Target::new();
    host.set_routes(args[1..].to_vec());

    let pause = Duration::new(60 * 60 * 24 * 7, 0);
    sleep(pause);
}
