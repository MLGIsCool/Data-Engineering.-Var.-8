import os
from datetime import datetime

import pandas as pd

from src.config_loader import load_config
from src.logger import get_error_logger, get_quality_logger
from src.parser import build_fetcher, parse, FIELDS
from src import quality_check

def save_incremental(df: pd.DataFrame, cfg: dict):
    if df.empty:
        print('Нет данных для сохранения.')
        return

    date_str = datetime.now().strftime('%Y-%m-%d')
    dir_path = os.path.join(cfg['paths']['data_dir'], date_str)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, cfg['csv_filename'])

    existing: set[str] = set()
    file_has_data = os.path.exists(file_path) and os.path.getsize(file_path) > 0
    if file_has_data:
        old = pd.read_csv(file_path, encoding='utf-8-sig')
        existing = set(old['name'].dropna().astype(str))

    df = df[FIELDS].copy()
    df_new = df[~df['name'].astype(str).isin(existing)]

    if df_new.empty:
        print(f'Новых товаров нет. Всего в файле: {len(existing)}')
        return

    encoding = 'utf-8-sig' if not file_has_data else 'utf-8'
    df_new.to_csv(
        file_path,
        mode='a',
        header=not file_has_data,
        index=False,
        encoding=encoding,
    )
    print(f'Добавлено {len(df_new)} новых. Всего в файле: {len(existing) + len(df_new)}')


def main() -> None:
    cfg = load_config('D:/PycharmProjects/ID1/config.yaml')
    err_log = get_error_logger(cfg['paths']['errors_log'])
    q_log = get_quality_logger(cfg['paths']['quality_log'])

    fetch = build_fetcher(cfg, err_log)

    try:
        html = fetch(cfg['url'])
        rows = parse(html, cfg['max_items'])
    except Exception as e:
        err_log.error(f"Не удалось получить {cfg['url']}: {e}")
        print('См. logs/scraper_errors.log')
        return

    df = pd.DataFrame(rows, columns=FIELDS)

    quality_check.check_and_log(df, q_log)

    df_fixed = quality_check.apply_fillna(df)

    save_incremental(df_fixed, cfg)


if __name__ == '__main__':
    main()