import logging, os

FMT = '%(asctime)s | %(levelname)s | %(message)s'
DATEFMT = "%Y-%m-%dT%H:%M:%S"

def get_logger(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lg = logging.getLogger('tradingview')
    lg.setLevel(logging.INFO)
    lg.handlers.clear()
    lg.propagate = False

    fh = logging.FileHandler(path, encoding='utf-8')
    fh.setFormatter(logging.Formatter(FMT, datefmt=DATEFMT))
    lg.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(FMT, datefmt=DATEFMT))
    lg.addHandler(sh)

    return lg
