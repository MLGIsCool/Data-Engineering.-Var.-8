import requests, backoff
from bs4 import BeautifulSoup as bs
from datetime import timezone, datetime

FIELDS = ['name', 'price', 'timestamp']

def build_fetcher(cfg, log):
  @backoff.on_exception(
    backoff.expo,
    (requests.ConnectionError, requests.Timeout, requests.HTTPError),
    max_tries=3,
    on_backoff=lambda d: log.error(
      f"Повтор #{d['tries']} для {d['args'][0] if d.get('args') else '?'}: {d['exception']}"),
    on_giveup=lambda d: log.error(
      f"Сдался после {d['tries']} попыток: {d['args'][0] if d.get('args') else '?'}"),
  )
  def fetch(url):
    response = requests.get(url, headers=cfg['headers'], timeout=(10, cfg['request']['timeout']))
    response.raise_for_status()
    return response.text
  return fetch

def parse(html, max_items):
  soup = bs(html, 'lxml')
  ts = datetime.now(timezone.utc).isoformat()
  data = []

  for p in soup.select('.price__new-val')[:20]:
    card = p
    while card.parent and not card.select_one('a[href]'): card = card.parent
    name = card.select_one('a[href]')
    meta = card.select_one('meta[itemprop="price"]')
    data.append({
        'name': name.get_text(strip=True) if name else None,
        'price': float(meta['content']) if meta else None,
        'timestamp': ts,
    })
  return data