use device_types::{Device, Subscriber};
use std::env;
use std::io::prelude::*;
use std::net::{TcpListener, TcpStream};

#[derive(Default)]
struct TcpEchoServer {
    port: String,
}

impl Device for TcpEchoServer {}
impl Subscriber for TcpEchoServer {
    fn loop_callback(&self, mut stream: TcpStream) {
        let mut buffer = [0; 128];

        let n = stream.read(&mut buffer);
        match n {
            Ok(msg_len) => {
                println!(
                    "Message received: {:?}",
                    String::from_utf8_lossy(&buffer[..msg_len])
                );
                stream.write("pong".as_bytes()).unwrap();
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

impl TcpEchoServer {
    pub fn new(port: String) -> TcpEchoServer {
        TcpEchoServer {
            port: port.to_string(),
        }
    }
}

fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();

    let server = TcpEchoServer::new("8080".to_string());
    server.set_routes(args[1..].to_vec());
    server.main_loop();

    Ok(())
}
