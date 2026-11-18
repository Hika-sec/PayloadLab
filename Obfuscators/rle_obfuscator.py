import os
import sys
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="RLE obfuscator for shellcode arrays")
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


def rle_compress(data):
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        j = i + 1
        while j < n and data[j] == data[i] and (j - i) < 255:
            j += 1
        out.append(j - i)
        out.append(data[i])
        i = j
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

    compressed = rle_compress(shellcode)

    base, ext = os.path.splitext(args.input)
    output_path = f"{base}_rle{ext or '.txt'}"

    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(format_c(compressed))

    print(f"[+] Output file: {output_path}  ({os.path.getsize(output_path)} bytes)")
    print(f"[+] Size before compression: {len(shellcode)} bytes")
    print(f"[+] Size after  compression: {len(compressed)} bytes")


if __name__ == "__main__":
    main()