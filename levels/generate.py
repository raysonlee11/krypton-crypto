#!/usr/bin/env python3
"""Build the Krypton levels with fresh random secrets.

Run once at container start by entrypoint.sh (as root).

  krypton0 -> base64           (encoding is not encryption)
  krypton1 -> Caesar / ROT-n   (brute force 25 shifts)
  krypton2 -> Vigenere         (unknown key length: Kasiski / index of coincidence)
  krypton3 -> repeating XOR    (known-plaintext attack)
  krypton4 -> final flag
"""
import base64
import os
import pwd
import secrets
import string
import subprocess
from pathlib import Path

ROOT = Path("/krypton")
PASS_DIR = Path("/etc/krypton_pass")
TEXT_DIR = Path("/opt/krypton/text")
UPPER = string.ascii_uppercase


def rand_upper(n):
    return "".join(secrets.choice(UPPER) for _ in range(n))


def caesar(text, shift):
    out = []
    for c in text:
        if c in UPPER:
            out.append(UPPER[(UPPER.index(c) + shift) % 26])
        else:
            out.append(c)
    return "".join(out)


def vigenere(text, key):
    """Encrypt letters only; keep spaces / punctuation (like the original Krypton)."""
    out, i = [], 0
    for c in text:
        if c in UPPER:
            k = UPPER.index(key[i % len(key)])
            out.append(UPPER[(UPPER.index(c) + k) % 26])
            i += 1
    # Classic style: strip everything, group into blocks of five
    s = "".join(out)
    return " ".join(s[j:j + 5] for j in range(0, len(s), 5))


def xor_repeat(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def write(path: Path, content, owner=None, mode=0o640):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)
    if owner:
        pw = pwd.getpwnam(owner)
        os.chown(path, 0, pw.pw_gid)
    os.chmod(path, mode)


def level_dir(n):
    d = ROOT / f"krypton{n}"
    d.mkdir(parents=True, exist_ok=True)
    pw = pwd.getpwnam(f"krypton{n}")
    os.chown(d, 0, pw.pw_gid)
    os.chmod(d, 0o750)          # only kryptonN can enter its own level dir
    return d


def main():
    ROOT.mkdir(exist_ok=True)
    os.chmod(ROOT, 0o711)
    PASS_DIR.mkdir(exist_ok=True)
    os.chmod(PASS_DIR, 0o711)

    pw = {0: "krypton0"}
    for n in range(1, 5):
        pw[n] = rand_upper(12)

    # ---------- krypton0 : base64 ----------
    d = level_dir(0)
    write(d / "README", (TEXT_DIR / "README0").read_text(), "krypton0")
    write(d / "krypton1", base64.b64encode(f"The password for krypton1 is {pw[1]}\n".encode()).decode() + "\n",
          "krypton0")

    # ---------- krypton1 : Caesar ----------
    d = level_dir(1)
    shift = secrets.choice([s for s in range(1, 26) if s != 13])
    write(d / "README", (TEXT_DIR / "README1").read_text(), "krypton1")
    plain1 = f"WELL DONE. CAESAR NEVER KEPT A SECRET FOR LONG. THE PASSWORD FOR KRYPTON TWO IS {pw[2]}"
    write(d / "krypton2", caesar(plain1, shift) + "\n", "krypton1")

    # ---------- krypton2 : Vigenere ----------
    d = level_dir(2)
    keylen = secrets.choice([5, 6, 7, 8])
    vkey = rand_upper(keylen)
    write(d / "README", (TEXT_DIR / "README2").read_text(), "krypton2")
    body = (TEXT_DIR / "vigenere_plain.txt").read_text().upper()
    body = body.replace("{PASSWORD}", " ".join(pw[3]))  # spell it out letter by letter
    write(d / "krypton3", vigenere(body, vkey) + "\n", "krypton2")

    # ---------- krypton3 : repeating-key XOR ----------
    d = level_dir(3)
    xkey = secrets.token_bytes(secrets.choice([6, 7, 8]))
    write(d / "README", (TEXT_DIR / "README3").read_text(), "krypton3")
    plain3 = (f"KRYPTON TRANSMISSION // priority: high // "
              f"Repeating a short key is the same as not having a key at all. "
              f"The password for krypton4 is {pw[4]} // end of transmission\n").encode()
    write(d / "krypton4.enc", xor_repeat(plain3, xkey).hex() + "\n", "krypton3")

    # ---------- krypton4 : the end ----------
    d = level_dir(4)
    flag = os.environ.get("FLAG") or f"FLAG{{kryp70_{secrets.token_hex(8)}}}"
    write(d / "README", (TEXT_DIR / "README4").read_text(), "krypton4")
    write(d / "flag.txt", flag + "\n", "krypton4")

    # ---------- account passwords ----------
    lines = "".join(f"krypton{n}:{pw[n]}\n" for n in range(5))
    subprocess.run(["chpasswd"], input=lines.encode(), check=True)
    for n in range(5):
        p = PASS_DIR / f"krypton{n}"
        p.write_text(pw[n] + "\n")
        u = pwd.getpwnam(f"krypton{n}")
        os.chown(p, u.pw_uid, u.pw_gid)
        os.chmod(p, 0o400)

    # admin-only answer sheet for instructors
    write(Path("/root/answers.txt"),
          "".join(f"krypton{n}: {pw[n]}\n" for n in range(5))
          + f"caesar shift: {shift}\nvigenere key: {vkey}\nxor key: {xkey.hex()}\nflag: {flag}\n",
          mode=0o600)


if __name__ == "__main__":
    main()
