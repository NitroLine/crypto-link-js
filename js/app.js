const CryptoJS = require("crypto-js");
const myHostname ='outliner.zapto.org';
const init = (xkey, xdata) => {
  const myKey = CryptoJS.enc.Utf8.parse(xkey); // Use a key with sufficient entropy
  if (location.hostname !== myHostname) {
    location = 'about:blank';
  }
  function decrypt(ciphertextStr, key) {
    const ciphertext = CryptoJS.enc.Base64.parse(ciphertextStr);
    const iv = ciphertext.clone();
    iv.sigBytes = 16;
    iv.clamp();
    ciphertext.words.splice(0, 4);
    ciphertext.sigBytes -= 16;
    const decrypted = CryptoJS.AES.decrypt({
      ciphertext: ciphertext
    }, key, {
      iv: iv
    });
    return decrypted.toString(CryptoJS.enc.Utf8);
  }

  const keys = decrypt(xdata, myKey).split(':');
  const debug = document.getElementById('debug')
  if(debug && debug.innerText === 'True'){
    console.log('KeyId ', keys[0]);
    console.log('key ', keys[1]);
  }

  var playerInstance = jwplayer("player");

  playerInstance.setup({
    playlist: [{
      sources: [{
        default: false,
        type: "dash",
        file: document.getElementById('file').innerText,

        drm: {
          clearkey: {
            keyId: keys[0],
            key: keys[1]
          }
        },
      }],
      label: "0",
    }],
    width: "100%",
    height: "100%",
    aspectratio: "16:9",
    autostart: true,
    cast: {},
    withCredentials: false,
    sharing: false
  });
}

init(document.getElementById('xkey').innerText, document.getElementById('xdata').innerText);



