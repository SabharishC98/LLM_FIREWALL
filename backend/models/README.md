# DistilBERT Classifier Checkpoint

Copy the files of your fine-tuned `distilbert-base-uncased` sequence classification model (e.g. from Google Colab output or ShadowLens checkpoint) into this folder.

The folder structure should contain:
- `config.json`
- `model.safetensors` or `pytorch_model.bin`
- `tokenizer.json`
- `tokenizer_config.json`
- `vocab.txt`
- `special_tokens_map.json`

If the model files are not found or loaded in this directory at startup, the system will fall back to using **Layer 1 (Rule-Based)** and **Layer 2 (Heuristic Analysis)**, reporting degraded mode in health checks.
