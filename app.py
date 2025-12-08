import os
import io
import cv2
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, jsonify
# Google Cloud APIのインポート
from google.cloud import vision
from google.cloud import translate_v2 as translate

# --- 1. アプリケーションとクライアントの初期化 ---

# Renderなどの環境でFlaskがテンプレートを認識できるように設定
app = Flask(__name__, 
            template_folder='.', 
            static_folder='static')

# Google Cloud API クライアントの初期化 (認証情報が環境変数で設定されている必要があります)
vision_client = vision.ImageAnnotatorClient()
translate_client = translate.Client()

# OpenCVの顔検出器の初期化 (カメラ検出機能用)
# Render環境ではパスの調整が必要な場合があります
FACE_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)


# --- 2. ウェブページを提供するルーティング ---

@app.route('/')
def home():
    """ホーム画面 (index.html) にリダイレクトまたはレンダリング"""
    return render_template('index.html')

@app.route('/realtime_image.html')
def realtime_image_page():
    """カメラ物体検出デモページを提供する"""
    return render_template('realtime_image.html')

@app.route('/realtime_translate_ocr.html')
def realtime_translate_ocr_page():
    """カメラOCR翻訳デモページを提供する"""
    return render_template('realtime_translate_ocr.html')


# --- 3. カメラ物体検出 API ---

@app.route('/detect_object', methods=['POST'])
def detect_object():
    """
    クライアントから画像を受け取り、OpenCVを使って顔検出を行うAPIエンドポイント
    (既存のカメラ検出機能)
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file sent'}), 400

    file = request.files['image']
    
    try:
        # 画像を読み込み、OpenCV形式に変換
        img_stream = io.BytesIO(file.read())
        img_pil = Image.open(img_stream)
        img_np = np.array(img_pil.convert('RGB'))
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # OpenCVによる顔検出
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        detected_rectangles = []
        for (x, y, w, h) in faces:
            detected_rectangles.append({'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)})

        return jsonify({
            'success': True,
            'message': f'{len(faces)}個の顔を検出しました。',
            'detections': detected_rectangles
        })

    except Exception as e:
        print(f"Error during detection: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# --- 4. OCR翻訳 API ---

@app.route('/ocr_and_translate', methods=['POST'])
def ocr_and_translate():
    """
    クライアントから画像を受け取り、OCRでテキストを抽出し、翻訳して返すAPIエンドポイント
    (新規のOCR翻訳機能)
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file sent'}), 400

    file = request.files['image']
    target_language = request.form.get('target', 'en') 
    source_language_hint = request.form.get('source', 'ja') 

    try:
        # 1. 画像データを読み込み
        content = file.read()
        image = vision.Image(content=content)

        # 2. Google Cloud Vision APIでOCRを実行
        response = vision_client.text_detection(
            image=image, 
            image_context={"language_hints": [source_language_hint]}
        )
        texts = response.text_annotations

        if not texts:
            return jsonify({
                'success': True, 
                'original_text': '', 
                'translated_text': '画像からテキストを検出できませんでした。'
            })

        detected_text = texts[0].description.strip()
        
        # 3. Google Cloud Translation APIで翻訳を実行
        translation_result = translate_client.translate(
            detected_text,
            target_language=target_language
        )
        
        translated_text = translation_result['translatedText']
        
        return jsonify({
            'success': True,
            'original_text': detected_text,
            'translated_text': translated_text
        })

    except Exception as e:
        print(f"OCR and Translation Error: {e}")
        return jsonify({'success': False, 'error': f'OCRまたは翻訳でエラーが発生しました: {e}'}), 500


# --- 5. アプリケーションの実行 (ローカルテスト用) ---

if __name__ == '__main__':
    # Render本番環境では gunicorn が起動するためこの部分は無視されます
    app.run(debug=True, port=os.getenv("PORT", 5000))