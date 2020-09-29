import subprocess
import time


def main():
    scenarios = [
                    './docker-compose/collect_ddos_3.yml',
                    './docker-compose/collect_ddos_5.yml',
                    './docker-compose/collect_norm_3.yml',
                    './docker-compose/collect_norm_5.yml'
                ]

    for file in scenarios:
        args = ['docker-compose', '-f', file, 'up', '-d']
        p = subprocess.run(args, capture_output=True)
        print(p.stdout)
        print(p.stderr)
        time.sleep(60 * 60 * 3)
        args = ['docker-compose', '-f', file, 'stop']
        p = subprocess.run(args, capture_output=True)
        print(p.stdout)
        print(p.stderr)


if __name__ == '__main__':
    main()
