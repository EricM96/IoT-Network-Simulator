use std::io::prelude::*;
use std::io::Result;
use std::net::TcpStream;
use std::thread;
use device_types::{Device, Publisher};
use std::env;

#[derive(Default)]
struct TcpEchoClient {
    peer: String
}

impl Device for TcpEchoClient {}
impl Publisher for TcpEchoClient {
    fn loop_callback(&self) {
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

impl TcpEchoClient {
    pub fn new(peer: String) -> TcpEchoClient {
        TcpEchoClient { peer: peer.to_string() }
    }
}

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();

    TcpEchoClient::new("echo-server:8080".to_string())
        .set_routes(args[1..].to_vec())
        .main_loop();

    Ok(())
}
