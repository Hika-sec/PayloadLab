__attribute__((section(".text")))
unsigned char cmp[] = < /*shellcode*/>;

const unsigned int CMP_SIZE = sizeof(cmp) - 1;
const unsigned int ORIG_SIZE = 324;

void rle_decompress(const unsigned char* src, unsigned int src_len, unsigned char* dst, unsigned int dst_len) {
    unsigned int si = 0;
    unsigned int di = 0;
    while (si + 1 < src_len && di < dst_len) {
        unsigned int count = src[si++];
        unsigned char val = src[si++];
        for (unsigned int i = 0; i < count && di < dst_len; i++) {
            dst[di++] = val;
        }
    }
}

int main() {
    static unsigned char buf[ORIG_SIZE];
    rle_decompress(cmp, CMP_SIZE, buf, ORIG_SIZE);
    (*(void(*)())(&buf))();
    return 0;
}