import os
import shutil
import zipfile
import pandas as pd
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def setup_layer2():
    print("\n--- [1] LAYER 2: HuggingFace Data SETUP ---")
    src_dir = "datasets/symptom-disease-dataset"
    dst_dir = "data/layer2"
    os.makedirs(dst_dir, exist_ok=True)
    
    files_to_copy = [
        "symptom-disease-train-dataset.csv",
        "symptom-disease-test-dataset.csv",
        "mapping.json"
    ]
    
    for f in files_to_copy:
        src = os.path.join(src_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, dst_dir)
            print(f"  Copied {f} to {dst_dir}")
        else:
            print(f"  [ERROR] Source {src} not found!")
            
    print("Layer2: HuggingFace data copied ✅")

def setup_mendeley():
    print("\n--- [2] LAYER 2: SymbiPredict (Mendeley) SETUP ---")
    zip_path = "datasets/SymbiPredict.zip"
    extract_to = "datasets/symbipredict_extracted"
    dst_dir = "data/layer2/mendeley"
    os.makedirs(dst_dir, exist_ok=True)
    
    if not os.path.exists(zip_path):
        print(f"  [ERROR] {zip_path} not found!")
        return

    # Extract
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        print(f"  Extracting {zip_path}...")
        zip_ref.extractall(extract_to)
        all_files = zip_ref.namelist()
        print(f"  Files found in zip: {len(all_files)}")
        # print(all_files) # Can be long
    
    # Move CSVs
    csv_found = False
    for root, _, files in os.walk(extract_to):
        for f in files:
            if f.endswith('.csv'):
                src = os.path.join(root, f)
                shutil.copy2(src, dst_dir)
                print(f"  Copied {f} to {dst_dir}")
                csv_found = src
                break # Just get the main one for analysis first
    
    if csv_found:
        print("\n  🔍 Analyzing Mendeley CSV:")
        df = pd.read_csv(csv_found)
        print(f"    * Columns: {df.columns.tolist()[:10]}...")
        print(f"    * Row count: {len(df)}")
        print(f"    * Sample rows:\n{df.head(2)}")
        
        # Bonus Analysis
        is_binary = any(df.iloc[0].apply(lambda x: str(x) in ['0', '1', '0.0', '1.0']))
        if is_binary:
            print("    * Format: Binary format detected (0/1)")
        else:
            print("    * Format: Text format detected")
            
        disease_col = None
        for col in ['Disease', 'Label', 'Condition', 'Target', 'disease', 'Label_Value']:
             if col in df.columns:
                 disease_col = col
                 break
        
        if disease_col:
            unique_diseases = df[disease_col].nunique()
            print(f"    * Unique diseases count: {unique_diseases}")
            print(f"    * Can it be merged with disease_profiles.json? Yes, likely via symptoms mapping.")
        else:
            # Maybe the first/last column is the label?
            # Or many columns are symptoms and row is disease?
            print("    * Disease column not clearly identified by common names.")
            
    print("Layer2: Mendeley SymbiPredict added ✅")

def setup_layer3():
    print("\n--- [3] LAYER 3: Synthea SETUP ---")
    zip_path = "datasets/synthea-master.zip"
    extract_to = "datasets/synthea_extracted"
    dst_dir = "data/layer3"
    os.makedirs(dst_dir, exist_ok=True)
    
    if not os.path.exists(zip_path):
        print(f"  [ERROR] {zip_path} not found!")
        return

    # Extract
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        print(f"  Extracting {zip_path}... (Wait as this is ~25MB)")
        zip_ref.extractall(extract_to)
        print("  Extraction complete.")

    # Search for modules
    module_path = os.path.join(extract_to, "src", "main", "resources", "modules")
    if os.path.exists(module_path):
        module_count = len([f for f in os.listdir(module_path) if f.endswith('.json')])
        print(f"  Found {module_count} disease modules in Synthea source.")
    
    # Check for output
    output_path = os.path.join(extract_to, "output", "csv")
    existing_outputs = []
    if os.path.exists(output_path):
        existing_outputs = [f for f in os.listdir(output_path) if f.endswith('.csv')]
        
    if not existing_outputs:
        readme_content = """Synthea needs Java to run. 
Command: cd datasets/synthea_extracted && ./run_synthea -p 100
Output will generate in output/csv/ folder"""
        with open(os.path.join(dst_dir, "README.txt"), "w") as f:
            f.write(readme_content)
        print("  ⚠️ Output folder empty. Generated README.txt with instructions.")
    else:
        for f in existing_outputs:
            shutil.copy2(os.path.join(output_path, f), dst_dir)
        print(f"  Copied {len(existing_outputs)} existing Synthea CSV outputs.")

    print("Layer3: Synthea structure ready ✅")

def final_audit():
    print("\n" + "="*50)
    print("   FINAL DATA FOLDER AUDIT")
    print("="*50)
    
    base = "data"
    structure = {
        "disease_profiles.json": os.path.exists(os.path.join(base, "disease_profiles.json")),
        "healthbridge.db": os.path.exists(os.path.join(base, "healthbridge.db")),
        "layer1/": os.path.exists(os.path.join(base, "layer1")),
        "layer2/": os.path.exists(os.path.join(base, "layer2")),
        "layer3/": os.path.exists(os.path.join(base, "layer3"))
    }
    
    for item, exists in structure.items():
        status = "✅" if exists else "❌"
        print(f"  {item:<30} {status}")
        if "layer" in item and exists:
            # Peek inside
            files = []
            for root, dirs, fs in os.walk(os.path.join(base, item.replace("/", ""))):
                for f in fs:
                    files.append(f)
            print(f"    (Contains {len(files)} files)")

if __name__ == "__main__":
    try:
        setup_layer2()
        setup_mendeley()
        setup_layer3()
        final_audit()
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Pipeline failed: {e}")
