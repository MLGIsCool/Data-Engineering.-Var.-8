import pandas as pd

def merge_csvs(data_dir, output_path):
    overview = pd.read_csv(f"{data_dir}\Обзор.csv")
    dynamics = pd.read_csv(f"{data_dir}\Динамика.csv")
    tech = pd.read_csv(f"{data_dir}\Теханализ.csv")

    for df in (overview, dynamics, tech):
        if 'name' in df.columns:
            df['pair_id'] = df['name'].str.replace('/', '', regex=False).str.replace(' ', '')
    merged = overview.merge(dynamics, on=['pair_id', 'name'], how='outer', suffixes=('', '_dyn'))
    merged = merged.merge(tech, on=['pair_id', 'name'], how='outer', suffixes=('', '_tech'))

    merged.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Итоговый файл: {output_path} ({len(merged)} строк)")
