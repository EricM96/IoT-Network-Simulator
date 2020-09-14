use std::io::prelude::*;
use std::net::{TcpListener, TcpStream};

fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 128];

    let n = stream.read(&mut buffer);
    match n {
        Ok(msg_len) => {
            let mut stream = TcpStream::connect("router:8080").unwrap();
            println!("Message received: {:?}", String::from_utf8_lossy(&buffer[..msg_len]));
            stream.write("pong".as_bytes()).unwrap();
            stream.flush().unwrap();
        }
        Err(error) => println!("Error encountered: {}", error),
    };
}

fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind("0.0.0.0:8080")?;

    println!("Listening for incoming connections");
    for stream in listener.incoming() {
        handle_connection(stream?);
    }
    Ok(())
}

