use std::io::prelude::*;
use std::net::{TcpListener, TcpStream};
use std::thread;

fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 128];

    let n = stream.read(&mut buffer);
    match n {
        Ok(msg_len) => {
            let pause = std::time::Duration::new(5, 0);
            thread::sleep(pause);
            let mut stream = TcpStream::connect("router:8080").unwrap();
            println!("Message received: {:?}", String::from_utf8_lossy(&buffer[..msg_len]));
            stream.write("ping".as_bytes()).unwrap();
            stream.flush().unwrap();
        }
        Err(error) => println!("Error encountered: {}", error),
    };
}

fn main() -> std::io::Result<()> {
    let start_connection = || {
        let pause = std::time::Duration::new(5, 0);
        thread::sleep(pause);

        let mut stream = TcpStream::connect("router:8080").unwrap();
        stream.write("ping".as_bytes()).unwrap();
        stream.flush().unwrap();
    };

    let listener = TcpListener::bind("0.0.0.0:8080")?;
    thread::spawn(start_connection);
    println!("Listening for incoming connections");
    for stream in listener.incoming() {
        handle_connection(stream?);
    }
    Ok(())
}

