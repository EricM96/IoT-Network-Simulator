from PIL import Image
from pathlib import Path
import sys


def main():
    path = sys.argv[1]
    path = Path.cwd() / Path(path)
    paths = path.glob('**/*.png')

    for path in paths:
        Image.open(path).convert('RGB').save(path)


if __name__ == '__main__':
    main()
