#include <stdio.h>
int main()
{
    int a, b;
    scanf("%d %d", &a, &b);
    while(1)
        printf("%d + %d = %d", a, b, a+b);
    return 0;
}