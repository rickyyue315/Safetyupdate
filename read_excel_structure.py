import pandas as pd

excel_file = 'Safety Stocks Calculation 1.xlsx'
df = pd.read_excel(excel_file, sheet_name=0)

print('=== All columns ===')
for i, col in enumerate(df.columns):
    print(f'{i}: {col}')

print('\n=== Sample data (first 15 rows, all columns) ===')
print(df.head(15).to_string())

print('\n=== Data types ===')
print(df.dtypes)

print('\n=== Looking for calculation patterns ===')
# 查看右側彙總區域的結構
print('\n=== Right side summary (columns 14-20) ===')
print(df.iloc[0:15, 14:21].to_string())
