#include <stdio.h>

// 线 -> 顺序栈、链栈、共享栈(多端)
// tip: 进制转换 -> 反取余幂 
void DecToBin(int num) {
    int stack[N], top = -1;
    while(num > 0) {
        stack[++top] = num % 2;
        num /= 2;
    }
    while(top != -1) {
        printf("%d", stack[top--]);
    }
}

