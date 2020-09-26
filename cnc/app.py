from flask import Flask, render_template, make_response, request
import socket

app = Flask(__name__)
network_state = {
    'garage_door': 'dormant',
    'lights': 'dormant',
    'motion_sensor': 'dormant',
    'refridgerator': 'dormant',
    'smart_home_controller': 'dormant',
    'thermostat': 'dormant',
    'weather_sensor': 'dormant',
}
duration = b'5'


def send_command(host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, 2828))
    cmd = b'1 ' + duration if network_state[host] == 'active' else b'0 0'
    sock.sendall(cmd)
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


def process_form(keys):
    for host in keys:
        network_state[host] = 'active' \
                if network_state[host] == 'dormant' else 'dormant'
        send_command(host)


@app.route('/', methods=['GET', 'POST'])
def root_controller():
    if request.method == 'POST':
        process_form(request.form.keys())
    return make_response(render_template(
        'index.html',
        network_state=network_state
    ))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
