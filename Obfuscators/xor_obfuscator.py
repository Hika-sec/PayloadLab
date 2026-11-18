import os
import sys
import argparse
XOR_KEY = 0x41

def parse_args():
    parser = argparse.ArgumentParser(description="XOR Obfuscator for shellcode arrays")
    parser.add_argument("-i", "--input", required=True, help="Input .txt file containing shellcode bytes")
    return parser.parse_args()

def read_shellcode(path):
    with open(path, "r") as f:
        data = f.read()
    data = data.replace('"', "").replace("\\x", "").replace("\\n", "").replace("\\r", "").replace("\\t", "")
    data = data.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
    if not data:
        raise ValueError("No shellcode data found in input file")
    try:
        return bytes.fromhex(data)
    except ValueError as e:
        raise ValueError(f"Invalid hex data in input file: {e}")

def xor_obfuscate(data, key):
    return bytes(b ^ (key & 0xFF) for b in data)

def format_c(data):
    chunks = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
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

    base, ext = os.path.splitext(args.input)
    output_path = f"{base}_xor{ext or '.txt'}"

    obfuscated = xor_obfuscate(shellcode, XOR_KEY)

    with open(output_path, "w") as f:
        f.write(format_c(obfuscated))

    print(f"[+] Output file: {output_path}  ({os.path.getsize(output_path)} bytes)")
    print(f"[+] XOR key:     0x{XOR_KEY:02x}")
    print(f"[+] Size before obfuscation: {len(shellcode)} bytes")
    print(f"[+] Size after  obfuscation: {len(obfuscated)} bytes")

if __name__ == "__main__":
    main()
