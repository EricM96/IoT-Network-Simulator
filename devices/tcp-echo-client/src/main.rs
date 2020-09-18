use std::io::prelude::*;
use std::net::TcpStream;
use std::process::Command;
use std::thread;

fn main() {
    Command::new("ip")
        .args(&[
            "route",
            "add",
            "172.18.0.3",
            "via",
            "172.18.0.2",
            "dev",
            "eth0",
        ])
        .output()
        .expect("Failed to add route");

    loop {
        let mut buffer = [0; 128];

        let pause = std::time::Duration::new(5, 0);
        thread::sleep(pause);
        let mut stream = TcpStream::connect("echo-server:8080").unwrap();
        stream.write("ping".as_bytes()).unwrap();
        let n = stream.read(&mut buffer).unwrap();
        println!(
            "Message received: {:?}",
            String::from_utf8_lossy(&buffer[..n])
        );
    }
}
