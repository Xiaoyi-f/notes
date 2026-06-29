#include <stdio.h>
#include <math.h>
#include <stdbool.h>

// 序列A、B本身有序 从大到小 归并到 新序列C 
void Merge(SqList A, SqList B, SqList &C) {
	int i = 0, j = 0, k = 0;
	while (i < A.length && j < B.length) {
		if (A.data[i] < B.data[j]) {
			C.data[k] = B.data[j];
			j++;k++;
		} else {
			C.data[k] = A.data[i];
			i++;k++;
		}
	}
	while (i < A.length) {
		C.data[k] = A.data[i];
		i++;k++;
	} 
	while (j < B.length) {
		C.data[k] = B.data[j];
		j++;k++;
	} 
	C.length = k;
} 

void Move(SqList &L) {
	int i = 0, j = L.length - 1; 
	while (i < j) {
		while (L.data[i] % 2 == 1) i++;
		while (L.data[j] % 2 == 0) j--;
		if (i < j) {
			swap(L.data[i], L.data[j]);
		}
	}
} 

int isPrime(int n) {
	if (n <= 1) return false;
	if (n == 2) return true;
	if (n % 2 == 0) return false;
	
	for (int i = 3; i <= sqrt(n); i += 2) {
		if (n % i == 0) return false;
	}
	return true;
}