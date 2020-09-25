#![allow(dead_code)]
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
    fn new(port: String) -> Bot {
        Bot { port: port }
    }

    fn main_loop(&self) {
        let listener = TcpListener::bind("0.0.0.0:".to_string() + &self.port)
            .expect("Failed to establish socket");

        for stream in listener.incoming() {
            self.loop_callback(stream.unwrap());
        }
    }

    fn loop_callback(&self, stream: TcpStream) {
        // TODO
    }
}

#[cfg(test)]
mod tests {}
