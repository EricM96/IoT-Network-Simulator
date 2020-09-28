use device_types::{Device, Publisher, Bot};
use rand::{self, Rng};
use std::env;
use std::io::prelude::*;
use std::net::TcpStream;
use std::thread;
use std::time::Duration;

//========================== Publisher Component ==================================================
#[derive(Default)]
/// A weather sensor that sends randomly generated temperature and humidity information to the
/// smart home controller at a set interval.
struct SmartFridge {
    /// Smart home controller address. Can be given as <hostname>:<port>.
    peer: String,
    /// Minimum temperature
    tmp_min: u8,
    /// Maximum temperature
    tmp_max: u8,
    /// Temperature random number generator
    tmp_rng: rand::rngs::ThreadRng,
    /// Interval length in seconds in which to send data to the smart home controller
    pause: Duration,
}

impl Device for SmartFridge {}
impl Publisher for SmartFridge {
    fn loop_callback(&mut self) {
        let mut buffer = [0; 128];

        let msg: String = format!(
            r#"{{"tmp": {}}}"#,
            self.rand_tmp(),
        );

        thread::sleep(self.pause);

        let mut stream = TcpStream::connect(&self.peer).unwrap();
        stream.write(msg.as_bytes()).unwrap();
        let n = stream.read(&mut buffer).unwrap();
        println!(
            "Message received: {:?}",
            String::from_utf8_lossy(&buffer[..n])
        );
    }
}

impl SmartFridge {
    pub fn new(
        peer: String,
        tmp_min: u8,
        tmp_max: u8,
        pause: u64,
    ) -> SmartFridge {
        SmartFridge {
            peer: peer,
            tmp_min: tmp_min,
            tmp_max: tmp_max,
            tmp_rng: rand::thread_rng(),
            pause: Duration::new(pause, 0),
        }
    }

    fn rand_tmp(&mut self) -> u8 {
        self.tmp_rng.gen_range(self.tmp_min, self.tmp_max)
    }
}

//========================== Main Method ==========================================================
fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();
    let bot_mode = args[1] == "true";

    // Start publisher loops with set routes
    let mut smart_fridge = SmartFridge::new(
        "smart_home_controller:8080".to_string(),
        34,
        40,
        1,
    );
    smart_fridge.set_routes(args[2..].to_vec());

    thread::spawn(move || {
        let bot = Bot::new("2828".to_string(), bot_mode);
        bot.main_loop();
    });
    smart_fridge.main_loop();

    Ok(())
}
