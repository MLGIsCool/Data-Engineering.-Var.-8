import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

ROW = 'tr[data-rowkey]'

def open_main_page(driver, cfg, log):
    log.info(f"Открываю главную: {cfg['base_url']}")
    try:
        driver.get(cfg['base_url'])
    except TimeoutException:
        log.warning("driver.get timeout, останавливаю загрузку вручную")
        try:
            driver.execute_script("window.stop();")
        except Exception:
            pass

    for _ in range(60):
        if driver.find_elements(By.CSS_SELECTOR, ROW):
            log.info("Таблица найдена")
            return True
        time.sleep(1)

    log.error(f"Таблица не появилась. page_source={len(driver.page_source)} символов")
    return False


def click_tab(driver, log, tab_text):
    xpaths = [
        f"//button[normalize-space()='{tab_text}']",
        f"//div[@role='tab'][normalize-space()='{tab_text}']",
        f"//*[self::button or self::div or self::span][normalize-space(text())='{tab_text}']",
    ]
    for xp in xpaths:
        try:
            for el in driver.find_elements(By.XPATH, xp):
                if el.is_displayed():
                    driver.execute_script("arguments[0].click();", el)
                    return True
        except Exception:
            continue
    log.warning(f"Кнопка «{tab_text}» не найдена — парсим то, что есть")
    return False


def parse_table(driver, tab, max_items):
    columns = tab['columns']
    rows = driver.find_elements(By.CSS_SELECTOR, ROW)
    result = []

    for row in rows:
        rowkey = row.get_attribute('data-rowkey') or ''
        tds = row.find_elements(By.CSS_SELECTOR, 'td')
        if not tds:
            continue

        first = [p.strip() for p in (tds[0].text or '').split('\n') if p.strip()]
        ticker = first[0] if first else ''
        name = first[1] if len(first) > 1 else ticker

        record = {
            'pair_id': rowkey.split(':')[-1].replace('/', '') if rowkey else ticker,
            'name': name,
        }

        values = [(td.text or '').strip() for td in tds[1:]]
        rest = [c for c in columns if c not in ('name', 'pair_id')]
        for i, col in enumerate(rest):
            record[col] = values[i] if i < len(values) else None

        for col in rest:
            if 'rating' in col:
                continue
            text = record.get(col) or ''
            cleaned = ''.join(ch for ch in text if ch.isdigit() or ch in '.,-').replace(',', '.')
            try:
                record[col] = float(cleaned) if cleaned else None
            except ValueError:
                record[col] = None

        result.append(record)

    return result[:max_items]


def scroll_until_enough(driver, log, cfg, target):
    last = 0
    for i in range(cfg['selenium']['max_scrolls']):
        cnt = len(driver.find_elements(By.CSS_SELECTOR, ROW))
        if cnt >= target or cnt == last:
            break
        last = cnt
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(cfg['selenium']['scroll_pause'])
        log.info(f"Скролл №{i+1}, строк: {cnt}")


def scrape_tab(driver, cfg, log, cache, tab_key):
    tab = cfg['tabs'][tab_key]
    cache_key = f"{cfg['base_url']}#{tab_key}"

    cached = cache.get(cache_key)
    if cached is not None:
        log.info(f"Использован кэш для «{tab['name']}» ({len(cached)} строк)")
        return cached[:cfg['max_items']]
    log.info(f"Переключаюсь на вкладку {tab['name']}")
    click_tab(driver, log, tab['tab_text'])
    time.sleep(5)


    try:
        WebDriverWait(driver, cfg['selenium']['wait_timeout']).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ROW))
        )
    except TimeoutException:
        log.error(f"{tab['name']}: строки не появились")
        return []

    scroll_until_enough(driver, log, cfg, cfg['max_items'])
    html = driver.page_source
    rows = parse_table(driver, tab, cfg['max_items'])

    if rows:
        cache.save(f"{cache_key}#rows", rows)
        cache.save_text(f"{cache_key}#html", html)
        log.info(f"«{tab['name']}» закэширован ({len(rows)} строк)")
    else:
        log.warning(f"«{tab['name']}» — 0 строк, кэш не сохраняем")

    log.info(f"Распарсено строк на {tab['name']}: {len(rows)}")
    return rows