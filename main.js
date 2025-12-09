let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let context = canvas.getContext('2d');
let stream = null;
let isProcessing = false; // 処理中フラグを追加

const API_URL = 'https://my-program-page.onrender.com/detect_object'; // あなたの公開URL

function startCamera() {
    // ... (カメラ起動コードはそのまま)

    // タイマーをクリアし、新しいリアルタイムループを開始
    if (stream) {
        // 以前の setInterval を使用している場合は、クリアが必要かもしれません
        // clearInterval(timerId); // timerId があればクリア
    }
    
    // **重要: setIntervalではなく、setTimeoutを使ったリアルタイムループを開始**
    if (stream) {
        realtimeLoop(); 
    }
}

// リアルタイム処理を制御する再帰的なループ関数
function realtimeLoop() {
    if (!stream) {
        console.log("Stream stopped.");
        return; // ストリームが閉じたら終了
    }

    // 処理中でなければ、フレームをサーバーに送信
    if (!isProcessing) {
        sendFrameToServer();
    }
    
    // 処理が完了するまで待つため、ここでは setTimeout は使わず、
    // sendFrameToServer の 'finally' ブロック内で次回ループを呼び出します。
}


async function sendFrameToServer() {
    // 処理中フラグを立てる
    isProcessing = true;

    // 1. ビデオフレームをキャンバスに描画
    // ... (キャンバス描画コードはそのまま)
    
    // 2. 画像データを取得
    // ... (formData作成コードはそのまま)

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData,
        });

        // 3. 応答の処理
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        
        // ... (結果の描画コードはそのまま)

    } catch (error) {
        console.error('Error sending frame to server:', error);
        // エラーが発生した場合も、処理を止めずにログに残す
    } finally {
        // **最も重要:** 処理が完了したらフラグを解除し、次のフレーム処理を0.1秒後に実行
        isProcessing = false;
        setTimeout(realtimeLoop, 100); // 100ms (1秒間に10フレーム)の間隔で再帰呼び出し
    }
}
