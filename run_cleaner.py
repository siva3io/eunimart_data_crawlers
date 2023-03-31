import os
import sys
import signal
import subprocess

WORKERS = os.cpu_count()

model_server_workers = int(os.environ.get('MODEL_SERVER_WORKERS', WORKERS))

def sigterm_handler(pids):
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass

    sys.exit(0)

def start_server():
    print('Starting the cleaner server with {} workers.'.format(model_server_workers))
    pids = []

    for _ in range(model_server_workers):
        gunicorn = subprocess.Popen(['python3','spider.py','-cmd', 'clean_data'])
        pids.append(gunicorn.pid)
    
    pids = set(pids)
    # signal.signal(signal.SIGTERM, sigterm_handler(pids))
    while True:
        pid, _ = os.wait()
    # If either subprocess exits, so do we.

    # sigterm_handler(pids)
    print('Inference server exiting')

# The main routine just invokes the start function.

if __name__ == '__main__':
    start_server()
