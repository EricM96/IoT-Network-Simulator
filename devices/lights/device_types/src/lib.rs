use std::process::Command;
use std::net::TcpStream;

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

#[cfg(test)]
mod tests {}
