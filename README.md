# redis-autocomplete

一个 Redis 自动补全的例子。

假设自动补全的内容只能是小写字母 a-z，不允许出现中文或者标点符号。

### 思路

当有序集合所有的成员分值都一样时，有序集合将根据成员名字进行排序（二进制顺序）