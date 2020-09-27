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


def send_command(host, rate: int, count: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, 2828))
    cmd = bytes(str(rate) + ' ' + str(count), 'utf-8')
    sock.sendall(cmd)
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


def process_form(form):
    rate = int(form['rate'])
    duration = int(form['duration'])
    count = rate * duration
    for host in form.keys():
        if host == 'duration' or host == 'rate':
            continue
        send_command(host, rate, count)


@app.route('/', methods=['GET', 'POST'])
def root_controller():
    if request.method == 'POST':
        process_form(request.form)
    return make_response(render_template(
        'index.html',
        network_state=network_state
    ))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
