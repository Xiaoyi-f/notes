#include <stdio.h>

// 线 -> 输入受限的双端队列、输出受限的双端队列、循环队列 
/*
front rear
rear = (rear + 1) % MaxSize
front = (front + 1) % MaxSize 
(rear + 1) % MaxSize == front 
front == rear 
count = (rear - front + MaxSize) % MaxSize  
*/ 
void YangHui(int n) {
    int queue[MAXSize], front = 0, rear = 0;
    queue[rear++] = 1;
    for (int i = 1; i <= n; i++) {
        int pre = 0;

        for (int j = 0; j < i; j++) {
            int cur = queue[front++];
            printf("%d ", cur);
            queue[rear++] = pre + cur;
            pre = cur;
        }
        
        queue[rear++] = 1;
        printf("\n");
    }
}


