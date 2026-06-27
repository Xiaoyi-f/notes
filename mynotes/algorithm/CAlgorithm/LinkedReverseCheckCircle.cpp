#include <stdio.h>
#include <stdlib.h>

int* dynamic = (int*)malloc(sizeof(int) * num);
int* zeronull = (int*)calloc(num, sizeof(int));
int* redynamic = (int*)realloc(dynamic, sizeof(int) * num);
free(dynamic); 

struct ListNode* reverseList(struct ListNode* head) {
	struct ListNode* prev = NULL;
	struct ListNode* curr = head;
	while (curr) {
		struct ListNode* next = curr -> next;
		curr -> next = prev;
		prev = curr;
		curr = next;
	}
	return prev;
}

int getNext(int x) {
    int d, y = 0;
    while (x) {
        d = x % 10;
        y += d * d;
        x /= 10;
    }
    return y;
}

bool isHappy(int n) {
    int p = n, q = n;
    while (q != 1) {
        p = getNext(p);
        q = getNext(getNext(q));
        if (p == q && p != 1) {
            return false;
        }
    }
    return true;
}
