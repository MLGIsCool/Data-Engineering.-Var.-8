import pandas as pd

FIELDS = ['name', 'price', 'timestamp']


def check_and_log(df, qlog):
    price_num = pd.to_numeric(df['price'], errors='coerce')
    name_str = df['name'].astype('string')

    for idx, row in df.iterrows():
        p = price_num.iloc[idx]
        n = name_str.iloc[idx]

        if pd.isna(p) or p <= 0:
            qlog.warning(
                f"Проблема с ценой: name={row['name']!r} | price={row['price']!r}"
            )
        if pd.isna(n) or str(n).strip() == '':
            qlog.warning(
                f"Пустое название: name={row['name']!r} | price={row['price']!r}"
            )


def apply_fillna(df):
    df = df.copy()

    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df.loc[df['price'] <= 0, 'price'] = pd.NA

    if df['price'].notna().any():
        df['price'] = df['price'].fillna(df['price'].mean())
    df['price'] = df['price'].round(2)

    df['name'] = df['name'].astype('string').str.strip()
    df.loc[df['name'] == '', 'name'] = pd.NA

    mode = df['name'].mode()
    if not mode.empty:
        df['name'] = df['name'].fillna(mode.iloc[0])

    return df[FIELDS]