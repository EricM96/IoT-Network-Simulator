use std::io::prelude::*;
use std::net::{TcpListener, TcpStream};

fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 128];

    let n = stream.read(&mut buffer);
    match n {
        Ok(msg_len) => {
            stream.write(&buffer[..msg_len]).unwrap();
            stream.flush().unwrap();
        }
        Err(error) => println!("Error encountered: {}", error),
    };

}

fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:8080")?;

    for stream in listener.incoming() {
        handle_connection(stream?);
    }
    Ok(())
}

