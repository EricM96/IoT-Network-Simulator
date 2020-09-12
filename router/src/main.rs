use std::collections::HashMap;
use std::io::prelude::*;
use std::net::{TcpListener, TcpStream};

fn handle_connection(mut stream: TcpStream, routing_table: &HashMap<String, String>) {
    let mut buffer = [0; 1028];

    let n = stream.read(&mut buffer);
    match n {
        Ok(msg_len) => {
            println!(
                "Message received: {:?}",
                String::from_utf8_lossy(&buffer[..msg_len])
            );
            println!("From: {:?}", stream.local_addr().unwrap());
            stream.write("pong".as_bytes()).unwrap();
            stream.flush().unwrap();
        }
        Err(error) => println!("Error encountered: {}", error),
    };
}

fn main() -> std::io::Result<()> {
    let mut routing_table: HashMap<String, String> = HashMap::new();
    routing_table.insert("echo-client".to_string(), "echo-server".to_string());
    routing_table.insert("echo-server".to_string(), "echo-client".to_string());

    let listener = TcpListener::bind("0.0.0.0:8080")?;

    println!("Listening for incoming connections");
    for stream in listener.incoming() {
        handle_connection(stream?, &routing_table);
    }
    Ok(())
}
