// 二分查找
int left = 0, right = n - 1;
while (left <= right) {
  int mid = left + (right - left) / 2;
  if (nums[mid] == target) return mid;
  else if (nums[mid] < target) left = mid + 1;
  else right = mid - 1;
}

// 二叉查找 
TreeNode* search(TreeNode* root, int target) {
  if (root == NULL || root -> val == target) return root;
  if (target < root -> val) return search(root -> left, target);
  else return search(root -> right, target);
}


