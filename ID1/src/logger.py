import logging
import os

FMT = '%(asctime)s | %(levelname)s | %(message)s'
DATEFMT = '%Y-%m-%dT%H:%M:%S'

def _make(name, filename, level):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    lg = logging.getLogger(name)
    lg.setLevel(level)
    lg.handlers.clear()
    lg.propagate = False
    fh = logging.FileHandler(filename, encoding='utf-8')
    fh.setFormatter(logging.Formatter(FMT, datefmt=DATEFMT))
    lg.addHandler(fh)
    return lg

def get_error_logger(path): return _make('scraper', path, logging.ERROR)

def get_quality_logger(path): return _make('quality', path, logging.WARNING)