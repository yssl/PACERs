#include <stdio.h>

int main(int argc, const char** argv)
{
    int stdinCount;
    int stdin[10];
    scanf("%d", &stdinCount);
    printf("stdinCount: %d\n", stdinCount);
    printf("stdin: ");
    for(int i=0; i<stdinCount-1; ++i)
    {
        scanf("%d", &stdin[i]);
        printf("%d ", stdin[i]);
    }
    printf("\n");
    printf("\n");

    printf("argc: %d\n", argc);
    for(int i=1; i<argc; ++i)
        printf("argv[%d]: %s, ", i, argv[i]);
    printf("\n");

    return 0;
}

