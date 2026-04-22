import sys
import os

print("Checking requirements...")
def check_requirements():
    required = ["torch", "transformers", "datasets", "sklearn", "accelerate", "pandas"]
    missing = []
    
    for req in required:
        try:
            if req == "sklearn":
                import sklearn
            else:
                __import__(req)
            print(f"[OK] found : {req}")
        except ImportError:
            print(f"[FAIL] missing: {req}")
            missing.append(req)
            
    if missing:
        pip_pkgs = [req if req != "sklearn" else "scikit-learn" for req in missing]
        print(f"\nPlease install missing packages: pip install {' '.join(pip_pkgs)}")
        print("Or run: pip install -r nlp_requirements.txt")
        sys.exit(1)

check_requirements()

import pandas as pd
import json
import torch
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from datasets import Dataset

# Setup paths relative to project root (training/)
# NOTE: This script lives in `training/training_scripts/`, but the actual datasets are in `training/data/`.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)  # -> training/
DATA_DIR = os.path.join(PROJECT_DIR, "data")
LAYER2_DIR = os.path.join(DATA_DIR, "layer2")

print("--------------------------------")
print("PART A - DATA PREPARATION")
print("--------------------------------\n")

# 1. Load HuggingFace CSV data
path_train = os.path.join(LAYER2_DIR, "symptom-disease-train-dataset.csv")
path_test = os.path.join(LAYER2_DIR, "symptom-disease-test-dataset.csv")
# `label_encodings.json` is stored in unused_legacy/archive in this repo.
# These IDs are used to map integer labels from the dataset CSVs into disease names.
path_mappings = os.path.join(PROJECT_DIR, "unused_legacy", "label_encodings.json")

df_train = pd.read_csv(path_train)
df_test  = pd.read_csv(path_test)

# Map integer labels directly to string disease names
with open(path_mappings, "r") as f:
    label_encodings = json.load(f)
disease_names = label_encodings.get("diseases", [])

def map_disease_id(val):
    try:
        idx = int(val)
        if 0 <= idx < len(disease_names):
            return disease_names[idx]
    except:
        pass
    return val

df_train['label'] = df_train['label'].apply(map_disease_id)
df_test['label']  = df_test['label'].apply(map_disease_id)

print(f"Train dataset shape: {df_train.shape}")
print(f"Test dataset shape: {df_test.shape}")

# 2. Load + Convert Mendeley binary data
path_mendeley = os.path.join(LAYER2_DIR, "mendeley", "symbipredict_2022.csv")
df_mendeley = pd.read_csv(path_mendeley)

def convert_row(row):
    symptoms = [col for col in df_mendeley.columns if col != 'prognosis' and row[col] == 1]
    return " ".join(symptoms)

df_mendeley_converted = pd.DataFrame()
df_mendeley_converted['text'] = df_mendeley.apply(convert_row, axis=1)
df_mendeley_converted['label'] = df_mendeley['prognosis']

print(f"\nMendeley rows converted: {len(df_mendeley_converted)}")
print(f"Unique diseases in Mendeley: {df_mendeley_converted['label'].nunique()}")

# 3. MERGE all three sources
df_combined = pd.concat([df_train, df_test, df_mendeley_converted], ignore_index=True)

# Normalize labels
df_combined['label'] = df_combined['label'].str.strip().str.title()
df_combined = df_combined.dropna(subset=['label'])
df_combined = df_combined[df_combined['label'] != '']

print(f"\nTotal combined rows: {len(df_combined)}")
print(f"Unique disease count: {df_combined['label'].nunique()}")
print("Top 10 diseases by frequency:")
print(df_combined['label'].value_counts().head(10))

out_combined = os.path.join(LAYER2_DIR, "combined_training_data.csv")
df_combined.to_csv(out_combined, index=False)
print(f"Saved: {out_combined}")

# 4. LABEL ENCODING
le = LabelEncoder()
df_combined["label_id"] = le.fit_transform(df_combined["label"])

total_classes = len(le.classes_)

id2label = {int(id_): label for label, id_ in zip(le.classes_, le.transform(le.classes_))}
label2id = {label: int(id_) for label, id_ in zip(le.classes_, le.transform(le.classes_))}

# Save mapping to data/label_mapping.json
label_mapping_json = {
    "label2id": label2id,
    "id2label": id2label,
    "total_classes": total_classes
}

mapping_file = os.path.join(DATA_DIR, "label_mapping.json")
with open(mapping_file, "w") as f:
    json.dump(label_mapping_json, f, indent=4)
print(f"Total classes found: {total_classes}")

# 5. TRAIN/TEST SPLIT
train_df, val_df = train_test_split(
    df_combined,
    test_size=0.2, 
    random_state=42
)

print(f"Train size: {len(train_df)}, Val size: {len(val_df)}")

print("--------------------------------")
print("PART B - MODEL TRAINING")
print("--------------------------------\n")

user_input = input("Training shuru karein? (y/n): ")
if user_input.lower() != 'y':
    print("Training aborted.")
    sys.exit(0)

# 6. CHECK GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\nDevice: {device}")
if device == "cpu":
    print("[WARN] CPU mode - training will take 2-3 hours")
    print("Tip: Google Colab free GPU use kar sakte hain")

# 7. TOKENIZER
MODEL_NAME = "bert-base-multilingual-cased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

max_length = 128

train_dataset_hf = Dataset.from_pandas(train_df)
val_dataset_hf = Dataset.from_pandas(val_df)

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=max_length)

train_dataset = train_dataset_hf.map(tokenize_function, batched=True)
val_dataset = val_dataset_hf.map(tokenize_function, batched=True)

# Prepare formats
train_dataset = train_dataset.rename_column("label_id", "labels")
val_dataset = val_dataset.rename_column("label_id", "labels")
train_dataset.set_format("torch", columns=["input_ids", "attention_mask", "labels"])
val_dataset.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

# 8. MODEL
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=total_classes,
    id2label=id2label,
    label2id=label2id
)

# 9. TRAINING ARGUMENTS
os.makedirs("models/bert_healthbridge", exist_ok=True)
training_args = TrainingArguments(
    output_dir="models/bert_healthbridge",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    logging_steps=50,
    warmup_ratio=0.1,
    weight_decay=0.01,
    fp16=True if device=="cuda" else False,
)

# 10. METRICS FUNCTION
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = logits.argmax(axis=-1)
    return {
        "accuracy": accuracy_score(labels, predictions),
        "f1": f1_score(labels, predictions, average="weighted")
    }

# 11. TRAIN
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)

print("\n[START] Starting training...\n")
trainer.train()

# 12. SAVE FINAL MODEL
save_path = "models/bert_healthbridge/final"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print(f"\n[OK] Model saved: {save_path}")

# 13. FINAL EVALUATION
print("\n[WAIT] Running Final Evaluation...")
results = trainer.evaluate()
print(f"Final Accuracy : {results['eval_accuracy']:.2%}")
print(f"Final F1 Score : {results['eval_f1']:.2%}")
