# coding=utf-8

import redis
import bisect
import uuid

conn = redis.Redis()

valid_characters = '`abcdefghijklmnopqrstuvwxyz{'       # 准备一个由已知字符串组成的列表

# 生成查询范围需要的两个值
def find_prefix_range(prefix):
    # 在字符列表中查找前缀字符所处的位置。
    posn = bisect.bisect_left(valid_characters, prefix[-1:])
    suffix = valid_characters[(posn or 1) - 1]
    return prefix[:-1] + suffix + '{', prefix + '{'

# 获取自动补全列表
def autocomplete_on_prefix(conn, guild, prefix):
    # 根据给定的查询前缀来计算出查询范围的起点和终点
    start, end = find_prefix_range(prefix);
    # 为起点和终点添加一个 uuid 防止误删
    identifier = str(uuid.uuid4())
    start += identifier
    end += identifier
    zset_name = 'members:' + guild

    # 将范围计算的起始元素和结束元素添加到有序集合中
    conn.zadd(zset_name, {start: 0, end: 0})
    pipeline = conn.pipeline(True)
    while 1:
        try:
            pipeline.watch(zset_name)
            sindex = pipeline.zrank(zset_name, start)
            eindex = pipeline.zrank(zset_name, end)
            erange = min(sindex + 9, eindex - 2)
            pipeline.multi()
            pipeline.zrem(zset_name, start, end)
            pipeline.zrange(zset_name, sindex, erange)
            items = pipeline.execute()[1]
            break
        except redis.exceptions.WatchError:
            continue
    return [item for item in items if '{' not in items]

# 加入工会
def join_guild(conn, guild, user):
    conn.zadd('members:' + guild, {user: 0})

# 离开工会
def leave_guild(conn, guild, user):
    conn.zrem('members:' + guild, user)

# # 添加工会
# join_guild(conn, 'test_guild', 'pchangl')

# # 获取自动补全列表
# print autocomplete_on_prefix(conn, 'test_guild', 'pch')

# # 离开工会
# leave_guild(conn, 'test_guild', 'collin')