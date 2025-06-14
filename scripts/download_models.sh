#!/bin/bash

# LLMモデルダウンロードスクリプト

set -e

echo "🤖 LLMモデルのダウンロードを開始します..."

# モデルディレクトリの作成
mkdir -p models

# ELYZA-japanese-Llama-2-7b-fast-instruct-q4_K_M.gguf
MODEL_URL="https://huggingface.co/mmnga/ELYZA-japanese-Llama-2-7b-fast-instruct-gguf/resolve/main/ELYZA-japanese-Llama-2-7b-fast-instruct-q4_K_M.gguf"
MODEL_FILE="models/ELYZA-japanese-Llama-2-7b-fast-instruct-q4_K_M.gguf"

if [ ! -f "$MODEL_FILE" ]; then
    echo "📥 ELYZAモデル(q4_K_M)をダウンロード中..."
    echo "   URL: $MODEL_URL"
    echo "   ファイルサイズ: 約 4.1GB"
    echo "   ⚠️  ダウンロードに時間がかかる場合があります"
    
    # wgetまたはcurlを使用してダウンロード
    if command -v wget &> /dev/null; then
        wget --progress=bar:force:noscroll -O "$MODEL_FILE" "$MODEL_URL"
    elif command -v curl &> /dev/null; then
        curl -L --progress-bar -o "$MODEL_FILE" "$MODEL_URL"
    else
        echo "❌ wget または curl が必要です"
        exit 1
    fi
    
    echo "✅ モデルダウンロード完了: $MODEL_FILE"
else
    echo "✅ モデルファイルは既に存在します: $MODEL_FILE"
fi

# より軽量なモデルもダウンロード（オプション）
echo ""
echo "🤔 より軽量なモデル(q2_K)もダウンロードしますか？ [y/N]"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    LIGHT_MODEL_URL="https://huggingface.co/mmnga/ELYZA-japanese-Llama-2-7b-fast-instruct-gguf/resolve/main/ELYZA-japanese-Llama-2-7b-fast-instruct-q2_K.gguf"
    LIGHT_MODEL_FILE="models/ELYZA-japanese-Llama-2-7b-fast-instruct-q2_K.gguf"
    
    if [ ! -f "$LIGHT_MODEL_FILE" ]; then
        echo "📥 軽量モデル(q2_K)をダウンロード中..."
        echo "   ファイルサイズ: 約 2.8GB"
        
        if command -v wget &> /dev/null; then
            wget --progress=bar:force:noscroll -O "$LIGHT_MODEL_FILE" "$LIGHT_MODEL_URL"
        else
            curl -L --progress-bar -o "$LIGHT_MODEL_FILE" "$LIGHT_MODEL_URL"
        fi
        
        echo "✅ 軽量モデルダウンロード完了: $LIGHT_MODEL_FILE"
    else
        echo "✅ 軽量モデルは既に存在します: $LIGHT_MODEL_FILE"
    fi
fi

# ダウンロード完了の確認
echo ""
echo "📋 ダウンロード済みモデル:"
ls -lh models/*.gguf 2>/dev/null || echo "   (モデルファイルが見つかりません)"

echo ""
echo "✅ モデルダウンロードが完了しました！"
echo ""
echo "🔧 設定方法:"
echo "   1. backend/.env ファイルを編集"
echo "   2. LLM_MODEL_PATH を設定:"
echo "      LLM_MODEL_PATH=./models/ELYZA-japanese-Llama-2-7b-fast-instruct-q4_K_M.gguf"
echo ""
echo "⚡ パフォーマンス比較:"
echo "   q4_K_M: 高品質、メモリ使用量多め (推奨)"
echo "   q2_K:   軽量、メモリ使用量少なめ (低スペック向け)"