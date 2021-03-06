use device_types::{Device, Publisher, Bot};
use rand::{self, Rng};
use std::env;
use std::io::prelude::*;
use std::net::TcpStream;
use std::thread;
use std::time::Duration;

//========================== Publisher Components =================================================
#[derive(Default)]
/// A weather sensor that sends randomly generated temperature and humidity information to the
/// smart home controller at a set interval.
struct MotionSensor {
    // Peer to publish data to
    peer: String,
    // Last message
    last_msg: String,
    // Generate random pauses between publications
    pause_min: u64,
    pause_max: u64,
    pause_rng: rand::rngs::ThreadRng,
}

impl Device for MotionSensor {}
impl Publisher for MotionSensor {
    fn loop_callback(&mut self) {
        let mut buffer = [0; 128];

        self.last_msg = if self.last_msg == "1" {
            "0".to_string()
        } else {
            "1".to_string()
        };
        let msg: String = format!(
            r#"{{"state": {}}}"#,
            self.last_msg,
        );

        thread::sleep(self.rand_pause());
        let mut stream = TcpStream::connect(&self.peer).unwrap();
        stream.write(msg.as_bytes()).unwrap();
        let n = stream.read(&mut buffer).unwrap();
        println!(
            "Message received: {:?}",
            String::from_utf8_lossy(&buffer[..n])
        );
    }
}

impl MotionSensor {
    pub fn new(
        peer: String,
        pause_min: u64,
        pause_max: u64,
    ) -> MotionSensor {
        MotionSensor {
            peer: peer.to_string(),
            last_msg: "0".to_string(),
            pause_min: pause_min,
            pause_max: pause_max,
            pause_rng: rand::thread_rng(),
        }
    }

    fn rand_pause(&mut self) -> Duration {
        let secs: u64 = self.pause_rng.gen_range(self.pause_min, self.pause_max);
        Duration::new(secs, 0)
    }
}

//========================== Main Method ==========================================================
fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();
    let bot_mode = args[1] == "true";

    let mut motion_sensor = MotionSensor::new("lights:8080".to_string(), 1, 30);
    motion_sensor.set_routes(args[2..].to_vec());

    thread::spawn(move || {
        let bot = Bot::new("2828".to_string(), bot_mode);
        bot.main_loop();
    });
    motion_sensor.main_loop();

    Ok(())
}
