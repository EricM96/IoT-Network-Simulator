use std::io::prelude::*;
use std::net::{TcpListener, TcpStream};
use std::process::Command;

fn handle_connection(mut stream: TcpStream) {
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

fn main() -> std::io::Result<()> {
    // Add route to publisher
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

    // Add subscriber endpoint
    let listener = TcpListener::bind("0.0.0.0:8080")?;

    // Subscriber loop
    println!("Listening for incoming connections");
    for stream in listener.incoming() {
        // Register handler
        handle_connection(stream?);
    }
    Ok(())
}

