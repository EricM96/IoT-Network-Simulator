use device_types::{Device, Publisher, Subscriber};
use rand::{self, Rng};
use std::env;
use std::io::prelude::*;
use std::net::{TcpListener, TcpStream};
use std::thread;
use std::time::Duration;

//========================== Subscriber Component =================================================
#[derive(Default)]
struct SmcServer {
    port: String,
}

impl Device for SmcServer {}
impl Subscriber for SmcServer {
    fn loop_callback(&self, mut stream: TcpStream) {
        let mut buffer = [0; 128];

        let n = stream.read(&mut buffer);
        match n {
            Ok(msg_len) => {
                println!(
                    "Message received: {:?}",
                    String::from_utf8_lossy(&buffer[..msg_len])
                );
                stream.write("Ok".as_bytes()).unwrap();
            }
            Err(error) => println!("Error encountered: {}", error),
        };
    }

    fn main_loop(&self) {
        let listener = TcpListener::bind("0.0.0.0:".to_string() + &self.port)
            .expect("Failed to establish socket");

        for stream in listener.incoming() {
            self.loop_callback(stream.unwrap());
        }
    }
}

impl SmcServer {
    pub fn new(port: String) -> SmcServer {
        SmcServer {
            port: port.to_string(),
        }
    }
}

//========================== Publisher Component ==================================================
#[derive(Default)]
/// A weather sensor that sends randomly generated temperature and humidity information to the
/// smart home controller at a set interval.
struct SmcClient {
    // Peer to publish data to
    peer: String,
    // Temperature generation
    tmp_min: u8,
    tmp_max: u8,
    tmp_rng: rand::rngs::ThreadRng,
    // Generate random pauses between publications
    pause_min: u64,
    pause_max: u64,
    pause_rng: rand::rngs::ThreadRng,
}

impl Device for SmcClient {}
impl Publisher for SmcClient {
    fn loop_callback(&mut self) {
        let mut buffer = [0; 128];

        let msg: String = format!(
            r#"{{"newTmp": {}}}"#,
            self.rand_tmp(),
        );

        thread::sleep(self.rand_pause());
        let mut stream = TcpStream::connect(&self.peer).unwrap();
        stream.write(msg.as_bytes()).unwrap();
        let n = stream.read(&mut buffer).unwrap();
        println!(
            "Message received: {:?}",
            String::from_utf8_lossy(&buffer[..n])
        );
    }
}

impl SmcClient {
    pub fn new(
        peer: String,
        tmp_min: u8,
        tmp_max: u8,
        pause_min: u64,
        pause_max: u64,
    ) -> SmcClient {
        SmcClient {
            peer: peer.to_string(),
            tmp_min: tmp_min,
            tmp_max: tmp_max,
            pause_min: pause_min,
            pause_max: pause_max,
            tmp_rng: rand::thread_rng(),
            pause_rng: rand::thread_rng(),
        }
    }

    fn rand_tmp(&mut self) -> u8 {
        self.tmp_rng.gen_range(self.tmp_min, self.tmp_max)
    }

    fn rand_pause(&mut self) -> Duration {
        let secs: u64 = self.pause_rng.gen_range(self.pause_min, self.pause_max);
        Duration::new(secs, 0)
    }
}

//========================== Main Method ==========================================================
fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();

    // Start publisher loop. There's no need to set the routes here since they are set by the
    // subscriber component
    thread::spawn(|| {
        let pause = Duration::new(2, 0);
        thread::sleep(pause);
        SmcClient::new("thermostat:8080".to_string(), 68, 72, 5, 15).main_loop();
    });

    // Start subscriber loops with set routes
    let smc = SmcServer::new("8080".to_string());
    smc.set_routes(args[1..].to_vec());
    smc.main_loop();

    Ok(())
}
