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
    """
    dimension = int(round(len(state) ** 0.5))  # 棋盘边长（3 或 4）
    distance = 0

    # 预先建立目标位置查找表，避免反复 index()
    goal_pos = {}
    for idx, val in enumerate(goal_state):
        goal_pos[val] = (idx // dimension, idx % dimension)

    for idx, val in enumerate(state):
        if val == 0:
            continue  # 不计空格
        cur_row = idx // dimension
        cur_col = idx % dimension
        goal_row, goal_col = goal_pos[val]
        distance += abs(cur_row - goal_row) + abs(cur_col - goal_col)

    return distance


def h_linear_conflict(state, goal_state):
    """
    曼哈顿距离 + 线性冲突惩罚（核心创新）。

    线性冲突定义：
    两个棋子 tj 和 tk 在同一行（或列），且它们的目标位置也在该行（或列），
    但当前顺序与目标顺序相反。

    每对冲突额外 +2（因为至少需要额外 2 步才能让对方通过）。
    这是数码问题中最强的可纳入启发函数之一，可大幅削减搜索树。
    """
    manhattan = h_manhattan(state, goal_state)
    dimension = int(round(len(state) ** 0.5))

    # 预先建立目标位置查找表
    goal_pos = {}
    for idx, val in enumerate(goal_state):
        if val != 0:
            goal_pos[val] = (idx // dimension, idx % dimension)

    conflict = 0

    # ---- 检查每一行的线性冲突 ----------------------------------------
    for row in range(dimension):
        row_tiles = []
        for col in range(dimension):
            idx = row * dimension + col
            val = state[idx]
            if val == 0:
                continue
            if val not in goal_pos:
                continue
            g_row, g_col = goal_pos[val]
            if g_row == row:  # 目标也在本行
                row_tiles.append((val, col, g_col))

        # 两两比较：当前列顺序与目标列顺序是否相反
        for i in range(len(row_tiles)):
            for j in range(i + 1, len(row_tiles)):
                val_i, cur_col_i, goal_col_i = row_tiles[i]
                val_j, cur_col_j, goal_col_j = row_tiles[j]

                if cur_col_i < cur_col_j and goal_col_i > goal_col_j:
                    conflict += 2
                elif cur_col_i > cur_col_j and goal_col_i < goal_col_j:
                    conflict += 2

    # ---- 检查每一列的线性冲突 ----------------------------------------
    for col in range(dimension):
        col_tiles = []
        for row in range(dimension):
            idx = row * dimension + col
            val = state[idx]
            if val == 0:
                continue
            if val not in goal_pos:
                continue
            g_row, g_col = goal_pos[val]
            if g_col == col:
                col_tiles.append((val, row, g_row))

        for i in range(len(col_tiles)):
            for j in range(i + 1, len(col_tiles)):
                val_i, cur_row_i, goal_row_i = col_tiles[i]
                val_j, cur_row_j, goal_row_j = col_tiles[j]

                if cur_row_i < cur_row_j and goal_row_i > goal_row_j:
                    conflict += 2
                elif cur_row_i > cur_row_j and goal_row_i < goal_row_j:
                    conflict += 2

    return manhattan + conflict


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


