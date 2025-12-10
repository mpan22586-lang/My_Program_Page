// DOM要素の取得
const loginForm = document.getElementById("loginForm");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const packetPayloadDiv = document.getElementById("packetPayload");
const encryptionToggle = document.getElementById("encryptionToggle");
const currentStatusSpan = document.getElementById("currentStatus");
const protocolStatusHeader = document.getElementById("protocolStatusHeader");
const applicationLayerStatus = document.getElementById(
  "applicationLayerStatus"
);

/**
 * ダミーの暗号化文字列を生成する関数。
 */
function generateEncryptedPayload(length) {
  const chars = "abcdef0123456789";
  let result = "";
  // 元のペイロードより長いダミー文字列を生成して、暗号化後のデータの増加を模擬
  const dummyLength = Math.max(50, length * 2);

  for (let i = 0; i < dummyLength; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  // パケットの開始が「暗号化されたデータ」であることを示すプレフィックスを付与
  return `[TLS Encrypted Data]\nData Stream: 0x${result}...`;
}

// --- フォーム送信時の処理 ---
loginForm.addEventListener("submit", function (event) {
  event.preventDefault(); // フォームの通常の送信を防ぐ

  const isEncrypted = encryptionToggle.checked;
  const username = encodeURIComponent(usernameInput.value);
  const password = encodeURIComponent(passwordInput.value);

  // 平文のペイロード
  const payloadClear = `username=${username}&password=${password}`;

  if (isEncrypted) {
    // HTTPSモードの場合
    const payloadEncrypted = generateEncryptedPayload(payloadClear.length);

    packetPayloadDiv.textContent = payloadEncrypted;
    packetPayloadDiv.classList.remove("payload-clear");
    packetPayloadDiv.classList.add("payload-encrypted");
  } else {
    // HTTPモードの場合
    packetPayloadDiv.textContent = payloadClear;
    packetPayloadDiv.classList.remove("payload-encrypted");
    packetPayloadDiv.classList.add("payload-clear");
  }

  // 念のためスクロールしてペイロードを表示
  packetPayloadDiv.scrollIntoView({ behavior: "smooth", block: "center" });
});

// --- トグルスイッチ切り替え時の処理 ---
encryptionToggle.addEventListener("change", function () {
  if (this.checked) {
    // HTTPS (暗号化あり) に切り替え
    currentStatusSpan.textContent = "HTTPS (安全)";
    currentStatusSpan.classList.remove("payload-clear");
    currentStatusSpan.classList.add("payload-encrypted");

    protocolStatusHeader.textContent = "HTTPS (暗号化あり)";
    protocolStatusHeader.classList.add("header-https");

    applicationLayerStatus.textContent = "TLSv1.3 (Encrypted)";

    // パケット表示をリセット（すぐに暗号文を表示）
    packetPayloadDiv.textContent = generateEncryptedPayload(50);
    packetPayloadDiv.classList.remove("payload-clear");
    packetPayloadDiv.classList.add("payload-encrypted");
  } else {
    // HTTP (暗号化なし) に切り替え
    currentStatusSpan.textContent = "HTTP (危険)";
    currentStatusSpan.classList.remove("payload-encrypted");
    currentStatusSpan.classList.add("payload-clear");

    protocolStatusHeader.textContent = "HTTP (暗号化なし)";
    protocolStatusHeader.classList.remove("header-https");

    applicationLayerStatus.textContent = "HTTP";

    // パケット表示をリセット（平文の警告を表示）
    packetPayloadDiv.textContent =
      "現在の設定は「HTTP（暗号化なし）」です。ログインボタンを押すと平文が表示されます。";
    packetPayloadDiv.classList.remove("payload-encrypted");
    packetPayloadDiv.classList.add("payload-clear");
  }
});
