(function () {
  var root = document.querySelector('[data-totp-secret]');
  if (!root) return;

  var secret = root.getAttribute('data-totp-secret') || '';
  var uri = root.getAttribute('data-totp-uri') || '';
  var input = document.getElementById('totp-input');
  var codeEl = document.getElementById('totp-code');
  var leftEl = document.getElementById('totp-left');
  var fillBtn = document.getElementById('totp-fill');

  if (uri) {
    var qrEl = document.getElementById('totp-qr');
    if (qrEl && !qrEl.firstChild) {
      var s = document.createElement('script');
      s.src = 'https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js';
      s.onload = function () {
        if (window.QRCode) {
          new QRCode(qrEl, { text: uri, width: 160, height: 160, correctLevel: QRCode.CorrectLevel.M });
        }
      };
      document.head.appendChild(s);
    }
  }

  if (!codeEl || !fillBtn || !window.crypto || !window.crypto.subtle) return;

  function base32ToBytes(b32) {
    var alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    var bits = '';
    b32 = b32.replace(/=+$/, '').toUpperCase();
    for (var i = 0; i < b32.length; i++) {
      var v = alphabet.indexOf(b32[i]);
      if (v < 0) continue;
      bits += v.toString(2).padStart(5, '0');
    }
    var bytes = [];
    for (var j = 0; j + 8 <= bits.length; j += 8) {
      bytes.push(parseInt(bits.slice(j, j + 8), 2));
    }
    return new Uint8Array(bytes);
  }

  function currentCode() {
    var counter = Math.floor(Date.now() / 1000 / 30);
    var msg = new ArrayBuffer(8);
    var dv = new DataView(msg);
    dv.setUint32(0, Math.floor(counter / 4294967296));
    dv.setUint32(4, counter >>> 0);
    return crypto.subtle
      .importKey('raw', base32ToBytes(secret), { name: 'HMAC', hash: 'SHA-1' }, false, ['sign'])
      .then(function (key) { return crypto.subtle.sign('HMAC', key, msg); })
      .then(function (buf) {
        var sig = new Uint8Array(buf);
        var offset = sig[sig.length - 1] & 0x0f;
        var bin = ((sig[offset] & 0x7f) << 24) | (sig[offset + 1] << 16) | (sig[offset + 2] << 8) | sig[offset + 3];
        return String(bin % 1000000).padStart(6, '0');
      });
  }

  function refresh() {
    currentCode().then(function (code) {
      codeEl.textContent = code;
      if (leftEl) leftEl.textContent = (30 - (Math.floor(Date.now() / 1000) % 30)) + 's';
    });
  }

  fillBtn.addEventListener('click', function () {
    if (input && codeEl.textContent !== '------') input.value = codeEl.textContent;
  });

  refresh();
  setInterval(refresh, 1000);
})();
