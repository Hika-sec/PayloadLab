import os
import sys
import argparse

KEY = b"\x73\x65\x63\x72\x65\x74"


def parse_args():
    parser = argparse.ArgumentParser(description="RC4 obfuscator for shellcode arrays")
    parser.add_argument("-i", "--input", required=True, help="Input .txt file containing shellcode bytes")
    return parser.parse_args()


def read_shellcode(path):
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    for token in ('"', "\\x", "\\n", "\\r", "\\t", " ", "\n", "\r", "\t", ",", ";"):
        data = data.replace(token, "")
    if not data:
        raise ValueError("No shellcode data found in input file")
    try:
        return bytes.fromhex(data)
    except ValueError as e:
        raise ValueError(f"Invalid hex data in input file: {e}")


def rc4_crypt(data, key):
    if not key:
        raise ValueError("RC4 key must not be empty")
    s = list(range(256))
    j = 0
    key_bytes = key if isinstance(key, (bytes, bytearray)) else key.encode("utf-8")

    for i in range(256):
        j = (j + s[i] + key_bytes[i % len(key_bytes)]) % 256
        s[i], s[j] = s[j], s[i]

    i = 0
    j = 0
    out = bytearray()
    for byte in data:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        k = s[(s[i] + s[j]) % 256]
        out.append(byte ^ k)
    return bytes(out)


def format_c(data):
    chunks = []
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        escaped = "".join(f"\\x{b:02x}" for b in chunk)
        chunks.append(f'"{escaped}"')
    return "\n".join(chunks)


def main():
    args = parse_args()

    if not os.path.isfile(args.input):
        print(f"[!] Input file not found: {args.input}")
        sys.exit(1)

    try:
        shellcode = read_shellcode(args.input)
    except ValueError as e:
        print(f"[!] {e}")
        sys.exit(1)

    obfuscated = rc4_crypt(shellcode, KEY)

    base, ext = os.path.splitext(args.input)
    output_path = f"{base}_rc4{ext or '.txt'}"

    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(format_c(obfuscated))

    print(f"[+] Output file: {output_path}  ({os.path.getsize(output_path)} bytes)")
    print(f"[+] Size before obfuscation: {len(shellcode)} bytes")
    print(f"[+] Size after  obfuscation: {len(obfuscated)} bytes")


if __name__ == "__main__":
    main()
