use device_types::{Device, Subscriber};
use std::env;
use std::io::prelude::*;
use std::net::{TcpListener, TcpStream};

//========================== Subscriber Component =================================================
#[derive(Default)]
struct GarageDoor {
    port: String,
}

impl Device for GarageDoor {}
impl Subscriber for GarageDoor {
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

impl GarageDoor {
    pub fn new(port: String) -> GarageDoor {
        GarageDoor {
            port: port.to_string(),
        }
    }
}

//========================== Main Method ==========================================================
fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();

    // Start subscriber loops with set routes
    let garage_door = GarageDoor::new("8080".to_string());
    garage_door.set_routes(args[1..].to_vec());
    garage_door.main_loop();

    Ok(())
}