import pandas as pd

excel_file = 'Safety Stocks Calculation 1.xlsx'
df = pd.read_excel(excel_file, sheet_name=0)

print('=== 左側數據 (實際店舖明細) ===')
left_cols = ['HK/ MO', '代號', '店舖', '舖類', '舖類細', '類別', 'CODE', 'Safety Stock', '貨場面積']
print(df[left_cols].head(20).to_string())

print('\n=== 右側數據 (按店舖類別彙總規則) ===')
right_cols = ['HK/ MO.1', '舖類.1', '貨場面積.1', '店舖數量', 'Safety Stock.1', 'ALL SHOP QTY needed']
summary_df = df[right_cols].dropna(subset=['HK/ MO.1'])
print(summary_df.to_string())

print('\n=== 計算邏輯分析 ===')
summary_df['計算結果'] = summary_df['店舖數量'] * pd.to_numeric(summary_df['Safety Stock.1'], errors='coerce')
print(summary_df[['HK/ MO.1', '舖類.1', '貨場面積.1', '店舖數量', 'Safety Stock.1', '計算結果', 'ALL SHOP QTY needed']].to_string())

print('\n=== 唯一的店舖類別組合 ===')
unique_classes = summary_df[['HK/ MO.1', '舖類.1', '貨場面積.1', 'Safety Stock.1']].drop_duplicates()
print(unique_classes.to_string())
