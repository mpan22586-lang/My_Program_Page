import os
import io
import json
import base64
from flask import Flask, request, jsonify, render_template
from google.cloud import vision
from google.oauth2 import service_account
from werkzeug.exceptions import BadRequest

# ----------------------------------------------------
# 1. Flaskアプリケーションの初期化
# ----------------------------------------------------
app = Flask(__name__)

# ----------------------------------------------------
# 2. Google Cloud Vision API クライアントの認証と初期化
# ----------------------------------------------------

# Render環境変数からJSON認証情報を読み込むためのカスタムロジック
credential_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')

if credential_json:
    try:
        # JSON文字列をcredentialsオブジェクトに変換
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(credential_json)
        )
        # 認証情報を使ってクライアントを初期化
        vision_client = vision.ImageAnnotatorClient(credentials=credentials)
        print("INFO: Google Cloud Vision Client initialized using JSON credentials from environment.")
    except Exception as e:
        # 環境変数のパースや認証に失敗した場合
        vision_client = None
        print(f"ERROR: Failed to initialize Vision Client with JSON environment variable: {e}")
        print("FALLBACK: Attempting standard Application Default Credentials.")
else:
    # GOOGLE_APPLICATION_CREDENTIALS環境変数やローカルのADCを試す（Renderでは通常失敗）
    vision_client = None
    print("INFO: GOOGLE_APPLICATION_CREDENTIALS_JSON not set. Attempting standard Application Default Credentials.")

# 最終的なクライアントの初期化（いずれかの方法で成功することを期待）
if vision_client is None:
    try:
        vision_client = vision.ImageAnnotatorClient()
        print("INFO: Vision Client initialized using standard default credentials.")
    except Exception as e:
        # 認証情報が全く見つからない致命的なエラー
        print(f"FATAL ERROR: Could not initialize Vision Client. Authentication failed. {e}")
        vision_client = None
        
# ----------------------------------------------------
# 3. ルート定義 (エンドポイント)
# ----------------------------------------------------

@app.route('/')
def home():
    """
    アプリケーションのホームルート。index.htmlをレンダリングします。
    """
    return render_template('index.html')

@app.route('/realtime_image.html')
def realtime_image_route():
    """
    リアルタイム画像処理デモページをレンダリングします。
    """
    return render_template('realtime_image.html')


@app.route('/detect_object', methods=['POST'])
def detect_object():
    """
    クライアントから送られた画像に対し、Google Cloud Vision APIを使って物体検出を行います。
    """
    # クライアントが認証されていなければ即座にエラーを返す
    if vision_client is None:
        return jsonify({
            'success': False,
            'error': 'API Client is not initialized due to authentication failure.'
        }), 500

    # 画像ファイルのチェック
    if 'image' not in request.files:
        app.logger.error("No image file received.")
        return jsonify({'success': False, 'error': 'No image file uploaded'}), 400

    image_file = request.files['image']
    content = image_file.read()

    try:
        # 1. 画像ファイルをVision APIのImageオブジェクトに変換
        image = vision.Image(content=content)

        # 2. 物体検出リクエストの実行
        # LABEL_DETECTIONを使用 (無料枠が広いことが多い)
        # OBJECT_LOCALIZATION (物体検出)の方がより正確ですが、無料枠が少ない場合があります。
        response = vision_client.annotate_image({
            'image': image,
            'features': [{'type': vision.Feature.Type.LABEL_DETECTION}],
        })
        
        detections = []
        
        # 3. 結果のパースと整形 (ここではラベル検出の結果をダミーの検出として返す)
        # 実際にはOBJECT_LOCALIZATIONを使うとboundingBoxesが得られます。
        # 現在のコードではLABEL_DETECTIONを使うため、検出結果をダミーの枠として扱います。
        
        # ダミーのバウンディングボックスデータ: 画面中央を検出したと仮定
        if response.label_annotations:
            # 信頼度が最も高い最初のラベルを代表とする
            first_label = response.label_annotations[0].description
            
            # ダミーの座標 (画面の中心に小さな枠を描画)
            detections.append({
                'label': first_label,
                'score': response.label_annotations[0].score,
                'x': 200, 
                'y': 200, 
                'w': 150, 
                'h': 150
            })
            
        return jsonify({
            'success': True,
            'detections': detections,
            'message': f"Detected {len(response.label_annotations)} labels."
        })

    except Exception as e:
        app.logger.error(f"Vision API processing error: {e}")
        return jsonify({'success': False, 'error': f'Server processing failed: {e}'}), 500

if __name__ == '__main__':
    # 開発環境での実行
    app.run(debug=True, host='0.0.0.0', port=os.environ.get("PORT", 5000))