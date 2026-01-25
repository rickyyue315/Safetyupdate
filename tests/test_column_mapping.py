"""
Test column name mapping functionality
"""
import sys
import pandas as pd
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_processor import DataProcessor
from core.constants import REQUIRED_INPUT_FIELDS


def test_column_name_mapping():
    """Test column name mapping functionality"""
    print("=" * 60)
    print("Testing Column Name Mapping Functionality")
    print("=" * 60)
    
    # Create test data with non-standard column names
    test_data = {
        'Article': ['110681212001', '110681212002'],
        'Site': ['HD09', 'HB29'],
        'Class': ['A1', 'A2'],
        'Last Month Sold Qty': [159, 86],
        'Last 2 Month': [58, 26],  # Non-standard column name
        'Supply source': ['2', '2'],  # Non-standard column name (lowercase s)
        'MOQ': [2, 2]
    }
    
    df_original = pd.DataFrame(test_data)
    
    print("\nOriginal column names:")
    print(df_original.columns.tolist())
    
    # Test normalization
    df_normalized = DataProcessor.normalize_column_names(df_original)
    
    print("\nNormalized column names:")
    print(df_normalized.columns.tolist())
    
    # Verify required fields exist
    print("\nChecking required fields:")
    for field in REQUIRED_INPUT_FIELDS:
        exists = field in df_normalized.columns
        status = "[OK]" if exists else "[FAIL]"
        print(f"  {status} {field}")
    
    # Verify data integrity
    print("\nData integrity check:")
    all_present = all(field in df_normalized.columns for field in REQUIRED_INPUT_FIELDS)
    if all_present:
        print("  [OK] All required fields are present")
    else:
        print("  [FAIL] Some required fields are missing")
        missing = [f for f in REQUIRED_INPUT_FIELDS if f not in df_normalized.columns]
        print(f"  Missing fields: {missing}")
    
    # Test actual file loading
    print("\n" + "=" * 60)
    print("Testing Actual File Loading")
    print("=" * 60)
    
    test_file = "data/input/110681212001_21Jan2026.XLSX"
    if Path(test_file).exists():
        try:
            df = DataProcessor.load_data(test_file)
            print(f"\n[OK] Successfully loaded file: {test_file}")
            print(f"   Records: {len(df)}")
            print(f"   Columns: {len(df.columns)}")
            print("\nFile column names:")
            for col in df.columns:
                print(f"  - {col}")
            
            # Check required fields
            print("\nChecking required fields:")
            for field in REQUIRED_INPUT_FIELDS:
                exists = field in df.columns
                status = "[OK]" if exists else "[FAIL]"
                print(f"  {status} {field}")
            
            # Verify
            all_present = all(field in df.columns for field in REQUIRED_INPUT_FIELDS)
            if all_present:
                print("\n[OK] All required fields are present, file can be processed!")
            else:
                print("\n[FAIL] Some required fields are missing")
                missing = [f for f in REQUIRED_INPUT_FIELDS if f not in df.columns]
                print(f"   Missing fields: {missing}")
        except Exception as e:
            print(f"\n[FAIL] Error loading file: {str(e)}")
    else:
        print(f"\n[WARN] Test file does not exist: {test_file}")
    
    print("\n" + "=" * 60)
    print("Test Completed")
    print("=" * 60)


if __name__ == "__main__":
    test_column_name_mapping()
