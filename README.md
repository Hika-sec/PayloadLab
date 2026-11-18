# Payload Obfuscation Research (Red Team)

This repository/folder contains small experiments created as part of **Red Team research into payload obfuscation techniques**. It includes simple obfuscators (Python) and corresponding loaders (C/C++) that transform, encode, or encrypt a shellcode payload and reconstruct/execute it in memory.

> **Disclaimer:** For educational purposes and **authorized security research / lab environments only**. Do not use against systems without explicit permission. The code executes raw shellcode and may be detected or blocked by security controls.

## Contents

| Component | Files | Description |
|---|---|---|
| Original sample | `simple.cpp` | Source/escaped-byte form of the x86 shellcode sample used for experiments. |
| XOR | `xor_obfuscator.py`, `loader_xor.cpp` | Single-byte XOR obfuscation (key `0x41`). Loader XOR-decodes in place and transfers control to the buffer. |
| RC4 | `rc4_obfuscator.py`, `loader_rc4.cpp` | RC4 stream obfuscation with a fixed embedded `KEY`. Loader performs RC4 KSA/PRGA decrypt and executes the buffer. |
| IP encoding | `ip_hash_obfuscator.py`, `loader_ip.cpp` | Encodes payload bytes as IPv4 dotted strings (4 bytes per address, zero-padded if needed). Loader parses and reconstructs bytes (IPfuscation-style encoding, not cryptographic hashing). |
| RLE | `rle_obfuscator.py`, `loader_rle.cpp` | Simple run-length encoding with `[count][byte]` pairs (`count` 1..255). Loader decodes into a fixed-size buffer and executes it. |
| ChaCha20 | `chacha20_obfuscator.py`, `loader_chacha20.cpp` | ChaCha20 stream cipher obfuscation (IETF/RFC 8439-style state: 32-bit counter, 96-bit nonce, 20 rounds) with fixed embedded `KEY`/`NONCE`/`COUNTER`. Loader generates keystream, XOR-decrypts, and executes. |


## Obfuscators (Python)

- **Input:** `-i/--input <file>` containing shellcode as C-style escaped bytes (e.g. `"\xfc\xe8..."` / `\xHH`). Parsers strip quotes, `\x`, whitespace, commas/semicolons as needed.
- **Output:** written automatically next to the input as `<basename>_<method><ext>` and basic stats are printed (sizes/counts). No custom output-path argument.
- **Usage examples:**

```bash
python xor_obfuscator.py -i shellcode.txt        # -> shellcode_obfuscated.txt
python rc4_obfuscator.py -i shellcode.txt        # -> shellcode_rc4.txt
python ip_hash_obfuscator.py -i shellcode.txt    # -> shellcode_ip.txt
python rle_obfuscator.py -i shellcode.txt        # -> shellcode_rle.txt
python chacha20_obfuscator.py -i shellcode.txt   # -> shellcode_chacha20.txt
python extract_shellcode.py                      # reads simple.cpp -> shellcode_input.txt
```

## Loaders (C/C++)

Each loader embeds the transformed payload (and constants/keys where applicable), reconstructs/decrypts it at runtime, and jumps to the buffer:

```c
(*(void(*)())(&buf))();
```

- **Build (example, MinGW/g++):**

```bash
g++ -O2 -o loader_xor.exe loader_xor.cpp
g++ -O2 -o loader_rc4.exe loader_rc4.cpp
g++ -O2 -o loader_ip.exe loader_ip.cpp
g++ -O2 -o loader_rle.exe loader_rle.cpp
g++ -O2 -o loader_chacha20.exe loader_chacha20.cpp
```

- **Architecture:** the sample shellcode is x86 (32-bit). Build and run with a matching architecture/OS.

## Notes & Limitations

- **Execution/memory:** loaders decode/decrypt and execute from their buffers without explicitly setting executable/writable memory protections (e.g. no `VirtualProtect`/RWX allocation). Depending on compiler, section placement (`.text`), and OS mitigations (DEP/NX), execution may fail or crash.
- **Payload behavior:** the sample payload may produce no console output and can depend on external conditions; a silent exit is not proof of success or failure.
- **RLE efficiency:** pairwise RLE expands data without runs (the sample grows from 324 to 614 bytes); it is included as a simple compression/encoding protocol example.
- **Security properties:** encodings (IP) and simple transforms (XOR/RLE) provide minimal resistance to analysis; RC4/ChaCha20 are used here with fixed embedded parameters for research/demonstration, not as a complete protection scheme.
- **Detection:** these are well-known patterns and may be flagged by EDR/AV; intended for controlled research and detection/analysis study.

## Purpose

Created to study and compare basic payload transformation, encoding, compression, and encryption/decryption flows (obfuscator ↔ loader) in a Red Team research context.
