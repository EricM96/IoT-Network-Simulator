use device_types::{Device, Publisher, Subscriber};
use std::env;
use std::io::prelude::*;
use std::net::{TcpListener, TcpStream};
use std::thread;
use std::time::Duration;

//========================== Subscriber Component =================================================
#[derive(Default)]
struct SmcServer {
    port: String,
}

impl Device for SmcServer {}
impl Subscriber for SmcServer {
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
                stream.flush().unwrap();
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

impl SmcServer {
    pub fn new(port: String) -> SmcServer {
        SmcServer {
            port: port.to_string(),
        }
    }
}

//========================== Publisher Component ==================================================
#[derive(Default)]
struct SmcClient {
    peer: String,
}

impl Device for SmcClient {}
impl Publisher for SmcClient {
    fn loop_callback(&mut self) {
        let mut buffer = [0; 128];

        let pause = std::time::Duration::new(5, 0);
        thread::sleep(pause);
        let mut stream = TcpStream::connect(&self.peer).unwrap();
        stream.write("ping".as_bytes()).unwrap();
        let n = stream.read(&mut buffer).unwrap();
        println!(
            "Message received: {:?}",
            String::from_utf8_lossy(&buffer[..n])
        );
    }
}

impl SmcClient {
    pub fn new(peer: String) -> SmcClient {
        SmcClient {
            peer: peer.to_string(),
        }
    }
}

//========================== Main Method ==========================================================
fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();

    // Start publisher loop. There's no need to set the routes here since they are set by the
    // subscriber component
    thread::spawn(|| {
        let pause = Duration::new(2, 0);
        thread::sleep(pause);
        SmcClient::new("host:port".to_string()).main_loop();
    });

    // Start subscriber loops with set routes
    let smc = SmcServer::new("8080".to_string());
    smc.set_routes(args[1..].to_vec());
    smc.main_loop();

    Ok(())
}
