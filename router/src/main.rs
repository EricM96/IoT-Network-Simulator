#![feature(proc_macro_hygiene, decl_macro)]

#[macro_use]
extern crate rocket;

use rocket_contrib::json::Json;
use serde::Serialize;
use std::process::Command;
use std::thread::sleep;
use std::time::Duration;

#[derive(Serialize)]
struct HostTraffic(u16, u16);

#[derive(Serialize)]
struct TrafficWindow {
    echo_client: HostTraffic,
    echo_server: HostTraffic,
}

#[get("/")]
fn index() -> Json<TrafficWindow> {
    let cmd_handle = Command::new("./get_packet_counts.sh")
        .output()
        .expect("Failed to get packet counts");

    let output = cmd_handle.stdout;
    let output: String = String::from_utf8_lossy(&output).to_string();
    let mut parts = output
        .split_whitespace()
        .map(|output| output.parse::<u16>());

    let window = TrafficWindow {
        echo_client: HostTraffic(
            parts.next().unwrap().unwrap(),
            parts.next().unwrap().unwrap(),
        ),
        echo_server: HostTraffic(
            parts.next().unwrap().unwrap(),
            parts.next().unwrap().unwrap(),
        ),
    };

    Json(window)
}

fn main() {
    let cmd_handle = Command::new("./set_packet_counts.sh")
        .output()
        .expect("Failed to run command");

    let output = cmd_handle.stdout;
    println!("{}", String::from_utf8_lossy(&output));

    rocket::ignite().mount("/", routes![index]).launch();
}
