use std::process::Command;
use std::time::Duration;
use std::thread::sleep;

fn main() -> std::io::Result<()> {
    let cmd_handle = Command::new("./set_packet_counts.sh")
        .output()
        .expect("Failed to run command");

    let output = cmd_handle.stdout;
    println!("{}", String::from_utf8_lossy(&output));

    // pause thread for one week
    let pause = Duration::from_secs(7 * 24 * 60 * 60);
    sleep(pause);

    Ok(())
}
