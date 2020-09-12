use std::io::prelude::*;
use std::net::TcpStream;
use std::time::Duration;

fn main() {
    let pause = Duration::new(5, 0);
    loop {
        let mut buffer = [0; 128];
        std::thread::sleep(pause);
        let mut stream = TcpStream::connect("router:8080").unwrap();
        stream.write("ping".as_bytes()).unwrap();

        let n = stream.read(&mut buffer);
        match n {
            Ok(msg_len) => {
                println!("Message received: {:?}", String::from_utf8_lossy(&buffer[..msg_len]));
                stream.write("pong".as_bytes()).unwrap();
                stream.flush().unwrap();
            }
            Err(error) => println!("Error encountered: {}", error),
        };
    }
}

