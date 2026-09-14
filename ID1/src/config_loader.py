import os, yaml

def load_config(path: str = 'D://PycharmProjects/ID1/config.yaml'):
    with open(path, 'r', encoding = 'utf-8') as f:
        cfg = yaml.safe_load(f)

    base = os.path.dirname(os.path.abspath(path))
    p = cfg['paths']

    p['base_dir'] = os.path.join(base, p.get('base_dir', '.'))
    p['data'] = os.path.join(p['base_dir'], p['data_dir'])
    p['logs_dir'] = os.path.join(p['base_dir'], p['logs_dir'])
    p['errors_log'] = os.path.join(p['logs_dir'], p['errors_log'])
    p['quality_log'] = os.path.join(p['logs_dir'], p['quality_log'])

    for key in ('data', "logs_dir"): os.makedirs(p[key], exist_ok = True)
    return cfg