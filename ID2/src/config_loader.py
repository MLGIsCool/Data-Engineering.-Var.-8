import os, yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG = os.path.join(BASE_DIR, "config.yaml")

def load_config(path: str = DEFAULT_CONFIG):
    with open(path, 'r', encoding = 'utf-8') as f:
        cfg = yaml.safe_load(f)

    base = os.path.dirname(os.path.abspath(path))
    p = cfg['paths']

    p['base_dir'] = os.path.join(base, p.get('base_dir', '.'))
    p['data_dir'] = os.path.join(p['base_dir'], p['data_dir'])
    p['cache_dir'] = os.path.join(p['base_dir'], p['cache_dir'])
    p['logs_dir'] = os.path.join(p['base_dir'], p['logs_dir'])
    p['errors_log'] = os.path.join(p['logs_dir'], p['errors_log'])

    for key in ('data_dir', "cache_dir", "logs_dir"): os.makedirs(p[key], exist_ok = True)
    return cfg