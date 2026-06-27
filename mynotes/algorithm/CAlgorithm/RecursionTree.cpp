#include <stdio.h>

// 递归
int handler(int n) {
    if (n == 1) return 1;
    return (handler(n - 1) + 1) * 2;
}
    
int handler(int i, int* nums, int len) {
    if (nums[i] >= (len - i)) return 0;
    return handler(i + nums[i], nums, len) + 1;
}

void handler(int start, int len) {
	if (len == m) {
		for (int i = 0; i < len; i++) {
			if (i > 0) printf(" ");
			printf("%d", arr[i]);
		}
		printf("\n");
        // 截断
		return ;
	}
	// 减枝
	if (n - start + 1 < m - len) return ;
	for (int i = start; i <= n; i++) {
		arr[len] = i;
		handler(i + 1, len + 1);
	}
}

// 汉诺塔 
void HanNuo(int n, char a, char b, char c) {
    if (n == 1) {
        printf("盘子1  %c -> %c\n", a, c);
        return;
    }
    HanNuo(n - 1, a, c, b);
    printf("盘子%d  %c -> %c\n", n, a, c);
    HanNuo(n - 1, b, a, c);
}

// Tree 节点度、树度、高度/深度、分支节点、叶子节点、森林
/*
n = n0 + n1 + n... = n1 + 2 * n2 + ... + 1
m次h高树: 
第i层最多节点数 -> m ** (i - 1)
最多总节点数 -> (m ** h - 1) / (m - 1) 
*/
 
// BT 
/*
n0 = n2 + 1 
满/完全BT:
分支节点逻辑编号 -> i <= n / 2
n为奇数 -> n1 = 0
n为偶数 -> n1 = 1 -> 逻辑编号(n / 2)
逻辑编号左右孩子 -> 2i 2i+1  
*/
// 前序(根)
(N)操作
(L)递归(bt -> lchild)
(R)递归(bt -> rchild) 

// 中序(根)
(L)递归(bt -> lchild)
(N)操作 
(R)递归(bt -> rchild)

// 后序(根)
(L)递归(bt -> lchild)
(R)递归(bt -> rchild)
(N)操作  

// BT构造 
单一序无法确定唯一树
先后无法确定唯一树 
前中确定唯一树
后中确定唯一树

// Tree(s) -> BT
兄弟连虚线、只留左一线 
森林头相连、首头为树头  
森林: m - 1 右下  
// BT -> Tree(s) 
左右孩连双亲、只留左一线 
抹掉右下线、各树依次转

// 线索二叉树
叶子下的空指针数 = 节点数 + 1 
节点的前驱依赖遍历方式得到的数组形式 
线索二叉树(二叉树线索化)即利用空指针(线索)指向节点的前驱和后继或扩展域(标签等方式)实现各个节点的线索的树 
没有前驱/后继则将线索指向空 
 
// 哈夫曼树与哈夫曼编码 
 
 
















 

