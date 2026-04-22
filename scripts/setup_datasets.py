import os
import shutil
import zipfile
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def create_folder_structure():
    """Sets up the folder structure: data/layer1/, data/layer2/, data/layer3/"""
    folders = ['data/layer1', 'data/layer2', 'data/layer3']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        logging.info(f"Directory ready: {folder}/")

def process_kaggle_dataset():
    """
    Simulates downloading the Kaggle dataset by extracting the provided zip file.
    Original target: itachi9604/disease-symptom-description-dataset
    """
    zip_path = "datasets/itachi9604_disease-symptom-description-dataset.zip"
    extract_target = "data/layer1/kaggle_disease_symptom"
    
    if not os.path.exists(zip_path):
        logging.error(f"Kaggle dataset zip not found at {zip_path}")
        return
        
    os.makedirs(extract_target, exist_ok=True)
    
    try:
        # Extract the dataset directly to layer1
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_target)
        logging.info("Extracted Kaggle dataset successfully into data/layer1/")
        
        # Verify and print row count
        dataset_csv = os.path.join(extract_target, "dataset.csv")
        if os.path.exists(dataset_csv):
            df = pd.read_csv(dataset_csv)
            logging.info(f"[SUCCESS] Kaggle 'dataset.csv' loaded. Row count: {len(df)}")
        else:
            logging.warning("dataset.csv not found in the Kaggle zip payload.")
            
    except Exception as e:
        logging.error(f"Failed to process Kaggle dataset: {e}")

def process_hf_dataset():
    """
    Simulates loading the HuggingFace dataset by copying the provided local dataset.
    Original target: duxprajapati/symptom-disease-dataset
    """
    hf_source_dir = "datasets/symptom-disease-dataset"
    hf_target_dir = "data/layer1/hf_symptom_disease"
    
    if not os.path.exists(hf_source_dir):
        logging.error(f"HuggingFace dataset folder not found at {hf_source_dir}")
        return
        
    os.makedirs(hf_target_dir, exist_ok=True)
    
    try:
        # Move/copy CSVs to layer1
        for item in os.listdir(hf_source_dir):
            if item.endswith('.csv'):
                src = os.path.join(hf_source_dir, item)
                dst = os.path.join(hf_target_dir, item)
                shutil.copy2(src, dst)
        
        logging.info("Loaded HuggingFace dataset successfully into data/layer1/")
        
        # Verify and print row counts
        train_csv = os.path.join(hf_target_dir, "symptom-disease-train-dataset.csv")
        test_csv = os.path.join(hf_target_dir, "symptom-disease-test-dataset.csv")
        
        if os.path.exists(train_csv):
            df_train = pd.read_csv(train_csv)
            logging.info(f"[SUCCESS] HuggingFace 'train' dataset loaded. Row count: {len(df_train)}")
            
        if os.path.exists(test_csv):
            df_test = pd.read_csv(test_csv)
            logging.info(f"[SUCCESS] HuggingFace 'test' dataset loaded. Row count: {len(df_test)}")
            
    except Exception as e:
        logging.error(f"Failed to process HuggingFace dataset: {e}")

if __name__ == "__main__":
    logging.info("Starting Dataset Setup Pipeline...")
    try:
        create_folder_structure()
        print("-" * 50)
        process_kaggle_dataset()
        print("-" * 50)
        process_hf_dataset()
        print("-" * 50)
        logging.info("Dataset Setup Pipeline Completed Successfully!")
    except Exception as e:
        logging.critical(f"Pipeline failed: {e}")
