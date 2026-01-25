"""
效能測試腳本 - 測量 Streamlit 應用程式啟動時間
"""
import time
import importlib
import sys
from pathlib import Path

# 記錄開始時間
start_time = time.time()
print("=" * 60)
print("開始效能測試...")
print("=" * 60)

# 測試 1: 基礎模組載入
print("\n[1] 測試基礎模組載入時間...")
module_start = time.time()

import streamlit as st
import io
from pathlib import Path

module_end = time.time()
print(f"    ✓ 基礎模組載入時間: {module_end - module_start:.3f} 秒")

# 測試 2: 設定模組載入（延遲載入）
print("\n[2] 測試設定模組載入時間（延遲載入）...")
settings_start = time.time()

from config.settings import Settings

settings_end = time.time()
print(f"    ✓ 設定模組載入時間: {settings_end - settings_start:.3f} 秒")

# 測試 3: 資料處理模組載入（延遲載入）
print("\n[3] 測試資料處理模組載入時間（延遲載入）...")
data_processor_start = time.time()

from core.data_processor import DataProcessor

data_processor_end = time.time()
print(f"    ✓ 資料處理模組載入時間: {data_processor_end - data_processor_start:.3f} 秒")

# 測試 4: 計算器模組載入（延遲載入）
print("\n[4] 測試計算器模組載入時間（延遲載入）...")
calculator_start = time.time()

from core.calculator import SafetyStockCalculator

calculator_end = time.time()
print(f"    ✓ 計算器模組載入時間: {calculator_end - calculator_start:.3f} 秒")

# 測試 5: pandas 模組載入（延遲載入）
print("\n[5] 測試 pandas 模組載入時間（延遲載入）...")
pandas_start = time.time()

import pandas as pd

pandas_end = time.time()
print(f"    ✓ pandas 模組載入時間: {pandas_end - pandas_start:.3f} 秒")

# 測試 6: 設定檔案載入（使用快取）
print("\n[6] 測試設定檔案載入時間（使用快取）...")
settings_load_start = time.time()

settings_file = "config/settings.json"
settings = Settings.load_from_file(settings_file)

settings_load_end = time.time()
print(f"    ✓ 設定檔案載入時間: {settings_load_end - settings_load_start:.3f} 秒")

# 測試 7: 第二次載入設定（測試快取效果）
print("\n[7] 測試第二次載入設定（測試快取效果）...")
settings_load2_start = time.time()

settings2 = Settings.load_from_file(settings_file)

settings_load2_end = time.time()
print(f"    ✓ 第二次設定載入時間: {settings_load2_end - settings_load2_start:.3f} 秒")

# 記錄總時間
total_time = time.time() - start_time
print("\n" + "=" * 60)
print("效能測試完成")
print("=" * 60)
print(f"總時間: {total_time:.3f} 秒")
print("\n優化建議:")
print("1. 如果基礎模組載入時間 > 1 秒，考慮減少頂層導入")
print("2. 如果設定載入時間 > 0.1 秒，考慮使用快取機制")
print("3. 如果 pandas 載入時間 > 0.5 秒，考慮延遲載入")
print("4. 比較第一次和第二次設定載入時間，評估快取效果")
print("=" * 60)
