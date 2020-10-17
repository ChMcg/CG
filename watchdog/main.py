import time, re, os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


class Handler(FileSystemEventHandler):
    def __init__(self, observer: Observer = None):
        self.observer = observer or None

    def on_created(self, event: FileCreatedEvent):
        if re.match(r'.*\.ui$', event.src_path):
            t = time.strftime('%Y-%m-%d_%H:%M', time.localtime())
            print(f"[{t}]", event.src_path)
            src: str = event.src_path
            new_src = src.replace('.ui', '.py')
            # apt install pyqt5-dev-tools
            os.system(f"pyuic5 $(pwd)/{src} > $(pwd)/{new_src}")


if __name__ == "__main__":
    a = Observer()
    a.schedule(Handler(), path='../ui/', recursive=True)
    a.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        a.stop()
    a.join()
