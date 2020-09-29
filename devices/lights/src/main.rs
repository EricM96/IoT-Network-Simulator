use device_types::{Device, Subscriber, Bot};
use std::thread;
use std::env;
use std::io::prelude::*;
use std::net::{TcpListener, TcpStream};

//========================== Subscriber Component =================================================
#[derive(Default)]
struct Lights {
    port: String,
}

impl Device for Lights {}
impl Subscriber for Lights {
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

impl Lights {
    pub fn new(port: String) -> Lights {
        Lights {
            port: port.to_string(),
        }
    }
}

//========================== Main Method ==========================================================
fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();
    let bot_mode: bool = args[1] == "true";

    // Start subscriber loops with set routes
    let lights = Lights::new("8080".to_string());
    lights.set_routes(args[2..].to_vec());

    thread::spawn(move || {
        let bot = Bot::new("2828".to_string(), bot_mode);
        bot.main_loop();
    });
    lights.main_loop();

    Ok(())
}
