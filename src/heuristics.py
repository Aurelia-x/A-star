"""
heuristics.py — 启发函数库

本文件包含两类启发函数：

【数码问题启发函数】（用于 8数码、15数码）
  接收参数：(state, goal_state)，其中 state 和 goal_state 都是一维 tuple

  1. h_zero(state, goal_state)
     - 零启发函数，始终返回 0
     - 用途：使 A* 退化为 Dijkstra 算法，用于性能对比测试

  2. h_misplaced(state, goal_state)
     - 错位棋子数启发函数
     - 计算不在目标位置的棋子数量（不计空格 0）
     - 用途：最弱的可纳入启发，作为基准对比

  3. h_manhattan(state, goal_state)
     - 曼哈顿距离启发函数
     - 计算所有棋子到各自目标位置的行列距离之和（不计空格 0）
     - 用途：数码问题的标准启发函数，效果良好

  4. h_linear_conflict(state, goal_state)
     - 曼哈顿距离 + 线性冲突惩罚（核心创新）
     - 检测同一行/列中顺序相反的棋子对，每对额外 +2 步惩罚
     - 用途：最强的可纳入启发函数，大幅削减搜索树

【迷宫问题启发函数】（用于二维网格迷宫寻路）
  接收参数：(state, goal_state)，其中 state 和 goal_state 都是 (row, col) 坐标 tuple

  5. h_maze_manhattan(state, goal_state)
     - 迷宫曼哈顿距离启发函数
     - 计算当前坐标到目标坐标的行列距离之和
     - 用途：网格迷宫中只允许上下左右移动时的标准启发函数
"""


# ====================================================================== #
#  数码问题（8数码 / 15数码）启发函数
# ====================================================================== #

def h_zero(state, goal_state):
    """
    零启发：始终返回 0。
    用于 Dijkstra 退化测试（A* 使用此函数时等价于 Dijkstra）。
    """
    return 0


def h_misplaced(state, goal_state):
    """
    错位棋子数：统计不在目标位置的棋子数量（不计空格 0）。
    这是最弱的可纳入启发，容易低估，导致扩展更多节点。
    """
    return sum(
        1
        for i in range(len(state))
        if state[i] != 0 and state[i] != goal_state[i]
    )


def h_manhattan(state, goal_state):
    """
    曼哈顿距离：所有棋子到各自目标位置的行列距离之和（不计空格 0）。
    这是数码问题的标准启发函数，可纳入且效果良好。
    公式：Σ |cur_row - goal_row| + |cur_col - goal_col|
    """
    dimension = int(round(len(state) ** 0.5))  # 棋盘边长（3 或 4）
    distance = 0

    # 预先建立目标位置查找表：value -> (row, col)，避免每步都调 index()
    goal_pos = {}
    for idx, val in enumerate(goal_state):
        goal_pos[val] = (idx // dimension, idx % dimension)

    # 遍历当前状态中每个非空格棋子，累加距离
    for idx, val in enumerate(state):
        if val == 0:
            continue  # 空格不计入距离
        cur_row = idx // dimension          # 当前行
        cur_col = idx % dimension           # 当前列
        goal_row, goal_col = goal_pos[val]  # 目标位置
        distance += abs(cur_row - goal_row) + abs(cur_col - goal_col)

    return distance


# 在函数外部定义一个缓存字典，避免每次调用重复生成目标位置字典
_goal_pos_cache = {}

def h_linear_conflict(state, goal_state):
    """
    高度优化的 曼哈顿距离 + 线性冲突 启发函数。
    保证 Admissibility（不超估），并将耗时压缩至最低。

    核心思路：
    1. 先算曼哈顿距离作为基础启发值
    2. 对于已处于目标行/列的棋子，检测它们之间是否"互相挡路"
       - 两个在同一目标行但目标列顺序相反的棋子，必然需要其中一个绕路
       - 每解决一对冲突至少需要额外 2 步（让开 + 回来）
    3. 总启发值 = 曼哈顿 + Σ(每行冲突×2) + Σ(每列冲突×2)
    """
    # 1. 从缓存中获取/计算目标位置 (避免千万次冗余计算)
    if goal_state not in _goal_pos_cache:
        dimension = int(round(len(goal_state) ** 0.5))
        pos_dict = {}
        for idx, val in enumerate(goal_state):
            if val != 0:
                pos_dict[val] = (idx // dimension, idx % dimension)
        _goal_pos_cache[goal_state] = (dimension, pos_dict)

    dimension, goal_pos = _goal_pos_cache[goal_state]

    manhattan = 0
    # 预分配行列收集器：row_tiles[r] 收集第 r 行中"已处于目标行的棋子"的目标列号
    row_tiles = [[] for _ in range(dimension)]
    col_tiles = [[] for _ in range(dimension)]

    # 2. 一次遍历，同时搞定曼哈顿距离和冲突前置收集
    for idx, val in enumerate(state):
        if val == 0:
            continue  # 空格不参与冲突检测

        cur_row, cur_col = idx // dimension, idx % dimension
        g_row, g_col = goal_pos[val]

        # 累加曼哈顿距离
        manhattan += abs(cur_row - g_row) + abs(cur_col - g_col)

        # 收集已位于目标行/列的棋子，用于后续冲突检测
        # "位于目标行"意味着该棋子只需要在本行内左右移动即可到达目标，无需换行
        if cur_row == g_row:
            row_tiles[cur_row].append(g_col)   # 记录它在目标行中的目标列号
        if cur_col == g_col:
            col_tiles[cur_col].append(g_row)   # 记录它在目标列中的目标行号

    conflict_penalty = 0

    # 3. 计算单行/列的线性冲突惩罚
    # 核心思想：在一行中，若棋子 A 的目标列 > 棋子 B 的目标列，
    # 而 A 当前在 B 的左边，则 A 要向右走、B 要向左走 → 两者互相挡路
    def count_line_conflicts(line):
        """
        贪心移除冲突最多的棋子，直到线段内无冲突。
        每移除一个棋子，额外增加 2 步惩罚（让开再回来）。
        """
        c = 0
        while True:
            inversions = [0] * len(line)
            # 统计每个棋子的冲突次数（逆序对数）
            for i in range(len(line)):
                if line[i] == -1: continue          # -1 表示该棋子已被移除
                for j in range(i + 1, len(line)):
                    if line[j] == -1: continue
                    # line[i] > line[j]：前面的棋子目标位置在后面 → 冲突
                    if line[i] > line[j]:
                        inversions[i] += 1
                        inversions[j] += 1

            # 找到当前参与冲突最多的棋子
            max_inv = max(inversions)
            if max_inv == 0:
                break  # 无冲突，结束

            # 贪心策略：移除冲突最多的棋子（假装它暂时让开）
            max_idx = inversions.index(max_inv)
            line[max_idx] = -1
            # 每移除一个棋子，付出 2 步代价：让出当前位(1) + 回到目标位(1)
            c += 2
        return c

    # 4. 对每一行和每一列执行冲突检测
    for row in row_tiles:
        if len(row) > 1:  # 至少 2 个棋子才可能冲突
            conflict_penalty += count_line_conflicts(row)

    for col in col_tiles:
        if len(col) > 1:
            conflict_penalty += count_line_conflicts(col)

    return manhattan + conflict_penalty


# ====================================================================== #
#  迷宫寻路启发函数（state / goal_state 为 (row, col) 坐标）
# ====================================================================== #

def h_maze_manhattan(state, goal_state):
    """
    迷宫曼哈顿距离：计算坐标之间的行列距离之和。

    适用于只允许上下左右移动的网格迷宫。
    state 和 goal_state 都是 (row, col) 形式的坐标元组。

    公式：|row1 - row2| + |col1 - col2|
    """
    return abs(state[0] - goal_state[0]) + abs(state[1] - goal_state[1])


