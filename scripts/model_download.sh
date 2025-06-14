#!/bin/bash
# download_model.sh - Llama-3-ELYZA-JP-8B-Q4モデルダウンロード

mkdir -p models
cd models

# Hugging Faceからダウンロード（例）
# 実際のURLは利用可能なモデルに応じて変更
wget -O Llama-3-ELYZA-JP-8B-Q4_K_M.gguf \
  "https://huggingface.co/elyza/Llama-3-ELYZA-JP-8B-q4_k_m-gguf/resolve/main/llama-3-elyza-jp-8b-q4_k_m.gguf"

echo "Model downloaded successfully!"