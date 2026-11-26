# Krypton – Cryptography Wargame

這是一個仿 OverTheWire Krypton 的密碼學關卡 Docker image。玩家透過 SSH 登入 Linux 環境，每破解一關就能拿到下一關帳號的密碼。

每次容器啟動時，**所有密碼、金鑰、密文都會重新隨機產生**，所以每個玩家或每個 instance 的答案都不一樣。

## 關卡

| 關卡 | 帳號 | 主題 | 學習重點 |
|---|---|---|---|
| 0 → 1 | `krypton0` / `krypton0` | Base64 | 編碼 ≠ 加密 |
| 1 → 2 | `krypton1` | Caesar cipher（隨機位移） | 25 把金鑰，暴力破解就好 |
| 2 → 3 | `krypton2` | Vigenère（金鑰長度 5–8，未知） | Kasiski／重合指數（IC）＋ 頻率分析 |
| 3 → 4 | `krypton3` | 重複金鑰 XOR（6–8 bytes） | 已知明文攻擊 |
| 4 | `krypton4` | 終點 | `cat flag.txt` |

關卡檔案放在 `/krypton/kryptonN/`（每一關的 `README` 有說明與提示）。每個帳號只能讀取自己這一關的目錄，以及 `/etc/krypton_pass/kryptonN`。

## 使用方式

```bash
docker run -d -p 2222:22 --name krypton ghcr.io/raysonlee11/krypton-crypto:latest
ssh krypton0@localhost -p 2222      # 密碼: krypton0
```

固定 flag（方便計分系統比對）：

```bash
docker run -d -p 2222:22 -e FLAG='FLAG{your_flag}' ghcr.io/raysonlee11/krypton-crypto:latest
```

沒有設定 `FLAG` 的話，就會隨機產生 `FLAG{kryp70_xxxxxxxxxxxxxxxx}`。

### 出題者：看答案

```bash
docker exec krypton cat /root/answers.txt
```

`solutions/solve.py` 是參考解答（請勿放進給玩家的環境）：

```bash
python3 solutions/solve.py 2 krypton3     # 自動算出 Vigenère 的金鑰長度和金鑰
```

## 專案結構

```
Dockerfile               Ubuntu 24.04 + openssh + python3 + xxd
entrypoint.sh            第一次啟動時產生關卡，接著啟動 sshd
levels/generate.py       產生隨機密碼與各關密文
levels/text/             各關 README 和 Vigenère 明文
solutions/solve.py       參考解答
.github/workflows/       push 到 main 時自動 build 並推到 ghcr.io
```

## 發佈

push 到 GitHub 的 `main` 分支後，GitHub Actions 會自動 build（amd64 與 arm64）並推到 `ghcr.io/<owner>/krypton-crypto`。第一次推上去之後，到 GitHub → Packages → krypton-crypto → Package settings，把 visibility 改成 **Public**。

## 授權

MIT
