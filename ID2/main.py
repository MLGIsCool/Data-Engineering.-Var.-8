import os
import pandas as pd

from src.config_loader import load_config
from src.logger import get_logger
from src.driver import build_driver
from src.parser import open_main_page, scrape_tab
from src.merge import merge_csvs
from src.cache import CacheManager

def save_csv(rows, path, columns):
    df = pd.DataFrame(rows)
    for col in columns + ['pair_id']:
        if col not in df.columns:
            df[col] = None

    numeric_cols = [c for c in columns
                    if c not in ('name', 'pair_id') and 'rating' not in c]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df[['pair_id'] + columns]
    df.to_csv(path, index=False, encoding='utf-8-sig', sep=',')
    print(f"Сохранено: {path} ({len(df)} строк)")


def main():
    cfg = load_config()
    log = get_logger(cfg['paths']['errors_log'])
    log.info('Сбор данных Tradingview')
    cache = CacheManager(cfg['paths']['cache_dir'], cfg['cache_ttl_minutes'])
    driver = build_driver(cfg)

    try:
        if not open_main_page(driver, cfg, log):
            log.error('Главная страница не загрузилась — выходим')
            return

        for tab_key in ('overview', 'dynamics', 'tech'):
            tab = cfg['tabs'][tab_key]
            rows = scrape_tab(driver, cfg, log, cache, tab_key)

            if not rows:
                log.warning(f"Нет данных для {tab['name']}")
                continue

            csv_path = os.path.join(cfg['paths']['data_dir'], f"{tab['name']}.csv")
            save_csv(rows, csv_path, tab['columns'])
            log.info(f"{tab['name']} сохранён: {csv_path}")

        csvs = [os.path.join(cfg['paths']['data_dir'], f"{cfg['tabs'][k]['name']}.csv")
                for k in ('overview', 'dynamics', 'tech')]
        if all(os.path.exists(p) for p in csvs):
            log.info('Объединение CSV в Итог.csv')
            merge_csvs(cfg['paths']['data_dir'],
                       os.path.join(cfg['paths']['data_dir'], 'Итог.csv'))
        else:
            log.warning('Не все CSV собраны — объединение пропущено')

    except Exception as e:
        log.error(f"Критическая ошибка: {e}")
        raise
    finally:
        driver.quit()
        log.info('Сбор завершён')


if __name__ == "__main__":
    main()