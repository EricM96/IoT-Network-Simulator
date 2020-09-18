use dns_lookup::lookup_addr;
use std::collections::HashMap;
use std::io::prelude::*;
use std::net::{IpAddr, TcpListener, TcpStream};
use std::process::Command;

fn handle_connection(
    mut stream: TcpStream,
    addr_book: &mut HashMap<IpAddr, String>,
    routing_table: &mut HashMap<String, String>,
) {
    let mut buffer = [0; 1028];

    // Resolve stream's Ip Address
    let peer: IpAddr = match stream.peer_addr() {
        Ok(addr) => addr.ip(),
        Err(_) => return,
    };
    println!("Connection from: {:?}", peer);

    // Resolve stream's hostname
    // Surely there must be a better way of doing this
    let peer: String = match addr_book.get(&peer) {
        Some(host_name) => host_name.to_string(),
        None => {
            let host_name = lookup_addr(&peer);
            match host_name {
                Ok(host_name) => {
                    addr_book.insert(peer, host_name.to_string());
                    host_name
                }
                Err(_) => return,
            }
        }
    };

    println!("Resolved to hostname: {:?}", peer);

    // Resolve stream's peer
    let peer = routing_table.get(&peer).unwrap();

    let n = stream.read(&mut buffer);
    match n {
        Ok(msg_len) => {
            println!(
                "Message received: {:?}",
                String::from_utf8_lossy(&buffer[..msg_len])
            );
            let mut stream = TcpStream::connect(peer).unwrap();
            match stream.write(&buffer[..msg_len]) {
                Ok(_) => (),
                Err(err) => {
                    print!("Error: {}", err);
                    return
                }
            };
            match stream.flush() {
                Ok(_) => (),
                Err(err) => {
                    print!("Error: {}", err);
                    return
                }
            };
        }

        Err(error) => println!("Error encountered: {}", error),
    };
}

fn main() -> std::io::Result<()> {
    let cmd_handle = Command::new("./set_packet_counts.sh")
                         .output()
                         .expect("Failed to run command");

    let output = cmd_handle.stdout;
    println!("{}", String::from_utf8_lossy(&output));

    let mut addr_book: HashMap<IpAddr, String> = HashMap::new();
    let mut routing_table: HashMap<String, String> = HashMap::new();

    routing_table.insert(
        "iot-network-simulator_echo-client_1.iot-network-simulator_iot".to_string(),
        "echo-server:8080".to_string(),
    );
    routing_table.insert(
        "iot-network-simulator_echo-server_1.iot-network-simulator_iot".to_string(),
        "echo-client:8080".to_string(),
    );

    let listener = TcpListener::bind("0.0.0.0:8080")?;

    println!("Listening for incoming connections");
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => handle_connection(stream, &mut addr_book, &mut routing_table),
            Err(_) => continue,
        }
    }
    Ok(())
}
