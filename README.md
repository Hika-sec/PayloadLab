# Payload Obfuscation Research (Red Team)

This repository contains small experiments created as part of **Red Team research into payload obfuscation techniques**. It includes simple obfuscators (Python) and corresponding loaders (C/C++) that transform, encode, or encrypt a shellcode payload and reconstruct/execute it in memory.

> **Disclaimer:** For educational purposes and **authorized security research / lab environments only**. Do not use against systems without explicit permission. The code executes raw shellcode and may be detected or blocked by security controls.

## Contents

| Component | Files | Description |
|---|---|---|
| Original sample | `Loaders/simple.cpp` | Minimal loader template executing a raw shellcode buffer. |
| XOR | `Obfuscators/xor_obfuscator.py`, `loader_xor.cpp` | Single-byte XOR obfuscation (key `0x41`). Loader XOR-decodes in place, copies to RWX memory, and transfers control. |
| RC4 | `Obfuscators/rc4_obfuscator.py`, `Loaders/loader_rc4.cpp` | RC4 stream obfuscation with a fixed embedded `KEY`. Loader performs RC4 decrypt, copies to RWX memory, and executes. |
| IP encoding | `Obfuscators/ip_hash_obfuscator.py`, `Loaders/loader_ip.cpp` | Encodes payload bytes as IPv4 dotted strings (4 bytes per address, zero-padded if needed). Loader parses/reconstructs bytes, copies to RWX memory, and executes (IPfuscation-style encoding, not cryptographic hashing). |
| RLE | `Obfuscators/rle_obfuscator.py`, `Loaders/loader_rle.cpp` | Simple run-length encoding with `[count][byte]` pairs (`count` 1..255). Loader decompresses, copies to RWX memory, and executes. |
| ChaCha20 | `Obfuscators/chacha20_obfuscator.py`, `Loaders/loader_chacha20.cpp` | ChaCha20 stream cipher obfuscation (IETF/RFC 8439-style state: 32-bit counter, 96-bit nonce, 20 rounds) with fixed embedded `KEY`/`NONCE`/`COUNTER`. Loader decrypts, copies to RWX memory, and executes. |

Payload data in the C/C++ sources is replaced with placeholders (`/* <shellcode> */`, `/* <ip list> */`) for publication; insert generated/transformed bytes before building.

## Obfuscators (Python)

- **Input:** `-i/--input <file>` containing shellcode as C-style escaped bytes (e.g. `"\xfc\xe8..."` / `\xHH`). Parsers strip quotes, `\x`, whitespace, commas/semicolons as needed.
- **Output:** written automatically next to the input as `<basename>_<method><ext>` and basic stats are printed (sizes/counts). No custom output-path argument.
- **Usage examples:**

```bash
python Obfuscators/xor_obfuscator.py -i shellcode.txt        # -> shellcode_obfuscated.txt
python Obfuscators/rc4_obfuscator.py -i shellcode.txt        # -> shellcode_rc4.txt
python Obfuscators/ip_hash_obfuscator.py -i shellcode.txt    # -> shellcode_ip.txt
python Obfuscators/rle_obfuscator.py -i shellcode.txt        # -> shellcode_rle.txt
python Obfuscators/chacha20_obfuscator.py -i shellcode.txt   # -> shellcode_chacha20.txt
```

## Loaders (C/C++)

Each loader embeds the transformed payload (and constants/keys where applicable), reconstructs/decrypts it, copies the result into executable memory allocated with `VirtualAlloc` (`PAGE_EXECUTE_READWRITE`), and transfers control:

```c
void *exec = VirtualAlloc(0, size, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
memcpy(exec, buf, size);
((void(*)())exec)();
```

- **Build (example, MinGW/g++):**

```bash
g++ -O2 -o loader_xor.exe loader_xor.cpp
g++ -O2 -o loader_rc4.exe Loaders/loader_rc4.cpp
g++ -O2 -o loader_ip.exe Loaders/loader_ip.cpp
g++ -O2 -o loader_rle.exe Loaders/loader_rle.cpp
g++ -O2 -o loader_chacha20.exe Loaders/loader_chacha20.cpp
g++ -O2 -o loader_simple.exe Loaders/loader_simple.cpp
```

- **Architecture:** the sample shellcode is x86 (32-bit). Build and run with a matching architecture/OS (Windows).

## Notes & Limitations

- **Execution/memory:** loaders copy decoded/decrypted payload into memory allocated as RWX (`PAGE_EXECUTE_READWRITE`) before execution. Behavior still depends on build settings, architecture, and OS mitigations/policies.
- **Payload behavior:** the sample payload may produce no console output and can depend on external conditions; a silent exit is not proof of success or failure.
- **RLE efficiency:** pairwise RLE expands data without runs (the sample grows from 324 to 614 bytes); it is included as a simple compression/encoding protocol example.
- **Security properties:** encodings (IP) and simple transforms (XOR/RLE) provide minimal resistance to analysis; RC4/ChaCha20 are used here with fixed embedded parameters for research/demonstration, not as a complete protection scheme.
- **Detection:** these are well-known patterns and may be flagged by EDR/AV; intended for controlled research and detection/analysis study.

## Purpose

Created to study and compare basic payload transformation, encoding, compression, and encryption/decryption flows (obfuscator ↔ loader) in a Red Team research context.
