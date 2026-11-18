import os
import sys
import argparse
import struct

KEY = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
NONCE = b"\x00\x00\x00\x00\x00\x00\x00\x4a\x00\x00\x00\x00"


def parse_args():
    parser = argparse.ArgumentParser(description="ChaCha20 obfuscator for shellcode arrays")
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


def rotl32(v, c):
    return ((v << c) & 0xffffffff) | (v >> (32 - c))


def quarter_round(x, a, b, c, d):
    x[a] = (x[a] + x[b]) & 0xffffffff; x[d] ^= x[a]; x[d] = rotl32(x[d], 16)
    x[c] = (x[c] + x[d]) & 0xffffffff; x[b] ^= x[c]; x[b] = rotl32(x[b], 12)
    x[a] = (x[a] + x[b]) & 0xffffffff; x[d] ^= x[a]; x[d] = rotl32(x[d], 8)
    x[c] = (x[c] + x[d]) & 0xffffffff; x[b] ^= x[c]; x[b] = rotl32(x[b], 7)


def chacha20_block(key, counter, nonce):
    state = [
        0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,
        struct.unpack_from("<I", key, 0)[0], struct.unpack_from("<I", key, 4)[0],
        struct.unpack_from("<I", key, 8)[0], struct.unpack_from("<I", key, 12)[0],
        struct.unpack_from("<I", key, 16)[0], struct.unpack_from("<I", key, 20)[0],
        struct.unpack_from("<I", key, 24)[0], struct.unpack_from("<I", key, 28)[0],
        counter,
        struct.unpack_from("<I", nonce, 0)[0], struct.unpack_from("<I", nonce, 4)[0],
        struct.unpack_from("<I", nonce, 8)[0],
    ]
    x = state[:]
    for _ in range(10):
        quarter_round(x, 0, 4, 8, 12)
        quarter_round(x, 1, 5, 9, 13)
        quarter_round(x, 2, 6, 10, 14)
        quarter_round(x, 3, 7, 11, 15)
        quarter_round(x, 0, 5, 10, 15)
        quarter_round(x, 1, 6, 11, 12)
        quarter_round(x, 2, 7, 8, 13)
        quarter_round(x, 3, 4, 9, 14)
    out = bytearray(64)
    for i in range(16):
        struct.pack_into("<I", out, i * 4, (x[i] + state[i]) & 0xffffffff)
    return bytes(out)


def chacha20_crypt(data, key, nonce, counter=1):
    out = bytearray()
    for i in range(0, len(data), 64):
        block = chacha20_block(key, counter + (i // 64), nonce)
        chunk = data[i:i + 64]
        for j, b in enumerate(chunk):
            out.append(b ^ block[j])
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

    obfuscated = chacha20_crypt(shellcode, KEY, NONCE)

    base, ext = os.path.splitext(args.input)
    output_path = f"{base}_chacha20{ext or '.txt'}"

    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(format_c(obfuscated))

    print(f"[+] Output file: {output_path}  ({os.path.getsize(output_path)} bytes)")
    print(f"[+] Size before obfuscation: {len(shellcode)} bytes")
    print(f"[+] Size after  obfuscation: {len(obfuscated)} bytes")


if __name__ == "__main__":
    main()