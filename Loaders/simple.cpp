__attribute__((section(".text")))
unsigned char buf[] = </*shellcode*/>;
            

int main()
{
    (*(void(*)())(&buf))();
}