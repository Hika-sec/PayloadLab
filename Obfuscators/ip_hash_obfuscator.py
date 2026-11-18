import os
import sys
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="IP hashing obfuscator for shellcode arrays")
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


def to_ipv4_strings(data):
    padded = bytearray(data)
    pad_len = (-len(padded)) % 4
    if pad_len:
        padded.extend(b"\x00" * pad_len)
    ips = []
    for i in range(0, len(padded), 4):
        chunk = padded[i:i + 4]
        ips.append(f"{chunk[0]}.{chunk[1]}.{chunk[2]}.{chunk[3]}")
    return ips, pad_len


def format_c(ips):
    lines = []
    for i, ip in enumerate(ips):
        suffix = "," if i < len(ips) - 1 else ""
        lines.append(f'"{ip}"{suffix}')
    return "\n".join(lines)


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

    ips, pad_len = to_ipv4_strings(shellcode)

    base, ext = os.path.splitext(args.input)
    output_path = f"{base}_ip{ext or '.txt'}"

    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(format_c(ips))

    print(f"[+] Output file: {output_path}  ({os.path.getsize(output_path)} bytes)")
    print(f"[+] Size before obfuscation: {len(shellcode)} bytes")
    print(f"[+] IPv4 entries: {len(ips)} (padded {pad_len} bytes)")
    print(f"[+] Size after  obfuscation: {len(ips) * 4} bytes")


if __name__ == "__main__":
    main()