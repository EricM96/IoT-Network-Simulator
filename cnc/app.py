from flask import Flask, render_template, make_response, request
from threading import Thread
import socket
import sys
import random

app = Flask(__name__)
network_hosts = [
    'garage_door',
    'lights',
    'motion_sensor',
    'refridgerator',
    'smart_home_controller',
    'thermostat',
    'weather_sensor',
]


def collection_loop():
    while True:
        for num_hosts in range(len(network_hosts)):
            generate_attack(num_hosts)


def generate_attack(num_hosts: int):
    rate = 20000
    count = 20000 * 600  # ~ 10 minutes
    active_bots = random.choices(network_hosts, k=num_hosts)
    workers = []
    print('Generating workers', flush=True)
    for bot in active_bots:
        worker = Thread(target=send_command_and_wait, args=(bot, rate, count))
        workers.append(worker)

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()
    print('Attack complete', flush=True)


def send_command_and_wait(host, rate: int, count: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, 2828))
    cmd = bytes(str(rate) + ' ' + str(count), 'utf-8')
    sock.sendall(cmd)
    _ = sock.recv(128)
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


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
    ))


if __name__ == '__main__':
    assert len(sys.argv) == 2
    mode = sys.argv[1]
    if mode == 'live':
        app.debug = True
        app.run(host='0.0.0.0', port=8000)
    elif mode == 'collect':
        collection_loop()
    else:
        print('Specify live or collect mode')
