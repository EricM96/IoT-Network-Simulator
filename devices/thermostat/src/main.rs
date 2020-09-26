use device_types::{Device, Subscriber, Bot};
use std::env;
use std::io::prelude::*;
use std::net::{TcpListener, TcpStream};
use std::thread;

//========================== Subscriber Component =================================================
#[derive(Default)]
struct Thermostat {
    port: String,
}

impl Device for Thermostat {}
impl Subscriber for Thermostat {
    fn loop_callback(&self, mut stream: TcpStream) {
        let mut buffer = [0; 128];

        let n = stream.read(&mut buffer);
        match n {
            Ok(msg_len) => {
                println!(
                    "Message received: {:?}",
                    String::from_utf8_lossy(&buffer[..msg_len])
                );
                stream.write("Ok".as_bytes()).unwrap();
            }
            Err(error) => println!("Error encountered: {}", error),
        };
    }

    fn main_loop(&self) {
        let listener = TcpListener::bind("0.0.0.0:".to_string() + &self.port)
            .expect("Failed to establish socket");

        for stream in listener.incoming() {
            self.loop_callback(stream.unwrap());
        }
    }
}

impl Thermostat {
    pub fn new(port: String) -> Thermostat {
        Thermostat {
            port: port.to_string(),
        }
    }
}

//========================== Publisher Component ==================================================
fn main() {
    let args: Vec<String> = env::args().collect();

    let therm = Thermostat::new("8080".to_string());
    therm.set_routes(args[1..].to_vec());

    thread::spawn(|| {
        let bot = Bot::new("2828".to_string());
        bot.main_loop();
    });
    therm.main_loop();
}
