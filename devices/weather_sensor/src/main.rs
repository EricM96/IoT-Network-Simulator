use device_types::{Device, Publisher};
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
struct WeatherSensor {
    /// Smart home controller address. Can be given as <hostname>:<port>.
    peer: String,
    /// Minimum temperature
    tmp_min: u8,
    /// Maximum temperature
    tmp_max: u8,
    /// Minimum humidity
    hmd_min: f32,
    /// Maximum humidity
    hmd_max: f32,
    /// Temperature random number generator
    tmp_rng: rand::rngs::ThreadRng,
    /// Humidity random number generator
    hmd_rng: rand::rngs::ThreadRng,
    /// Interval length in seconds in which to send data to the smart home controller
    pause: Duration,
}

impl Device for WeatherSensor {}
impl Publisher for WeatherSensor {
    fn loop_callback(&mut self) {
        let mut buffer = [0; 128];

        let msg: String = format!(
            r#"{{"tmp": {}, "hmd": {:.2}}}"#,
            self.rand_tmp(),
            self.rand_hmd()
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

impl WeatherSensor {
    pub fn new(
        peer: String,
        tmp_min: u8,
        tmp_max: u8,
        hmd_min: f32,
        hmd_max: f32,
        pause: u64,
    ) -> WeatherSensor {
        WeatherSensor {
            peer: peer.to_string(),
            tmp_min: tmp_min,
            tmp_max: tmp_max,
            hmd_min: hmd_min,
            hmd_max: hmd_max,
            tmp_rng: rand::thread_rng(),
            hmd_rng: rand::thread_rng(),
            pause: Duration::new(pause, 0),
        }
    }

    fn rand_tmp(&mut self) -> u8 {
        self.tmp_rng.gen_range(self.tmp_min, self.tmp_max)
    }

    fn rand_hmd(&mut self) -> f32 {
        self.hmd_rng.gen_range(self.hmd_min, self.hmd_max)
    }
}

//========================== Main Method ==========================================================
fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();

    // Start publisher loops with set routes
    let mut weather_sensor =
        WeatherSensor::new("smart_home_controller:8080".to_string(), 46, 75, 0.53, 0.85, 5);
    weather_sensor.set_routes(args[1..].to_vec());
    weather_sensor.main_loop();

    Ok(())
}

