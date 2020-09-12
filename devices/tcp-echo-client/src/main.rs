use std::io::prelude::*;
use std::net::TcpStream;
use std::time::Duration;

fn main() {
    let pause = Duration::new(5, 0);
    loop {
        let mut stream = TcpStream::connect("127.0.0.1:8080").unwrap();
        stream.write("ping".as_bytes()).unwrap();
        std::thread::sleep(pause);
    }
}

