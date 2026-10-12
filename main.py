import os
import sys

from campusflow.cli import run

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "tickets.json")

if __name__ == "__main__":
    sys.exit(run(DATA_PATH))
