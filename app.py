from flask import Flask, render_template_string

# Flaskアプリケーションのインスタンスを作成 (WSGIオブジェクト)
app = Flask(__name__)

# ホームページ (ルート /) にアクセスがあったときの処理
@app.route('/')
def home():
    # HTMLの内容を直接返す
    html_content = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>私のWebページ</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                margin-top: 50px; 
                background-color: #f0f0f0; 
            }
            h1 {
                color: #333;
            }
        </style>
    </head>
    <body>
        <h1>🎉 デプロイ成功！ 🎉</h1>
        <p>これはPygameではなく、PythonのFlaskを使ったWebアプリケーションです。</p>
        <p>これでRenderへのデプロイ準備が整いました。</p>
    </body>
    </html>
    """
    return render_template_string(html_content)

# このファイルが直接実行されたとき (ローカルテスト用)
if __name__ == '__main__':
    app.run(debug=True)