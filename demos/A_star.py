import heapq
import time

# 定义节点类
class Node:
    def __init__(self, state, parent=None, g=0, h=0):
        self.state = state      # 当前状态，用一维Tuple表示，例如 (2, 8, 3, 1, 0, 4, 7, 6, 5)
        self.parent = parent    # 父节点
        self.g = g              # 实际代价
        self.h = h              # 启发值
        self.f = g + h          # 评估值

    # 为了让 heapq (优先队列) 知道如何比较节点，重写小于号方法
    def __lt__(self, other):
        return self.f < other.f

    # 打印格式
    def __str__(self):
        s = ""
        for i in range(3):
            s += str(self.state[i*3 : i*3+3]) + "\n"
        return s

# 1. 计算逆序数并判断是否可解
def is_solvable(start_state, goal_state):
    def get_inversions(state):
        inv_count = 0
        # 忽略 0 (空格)
        state_list = [x for x in state if x != 0]
        # 外层循环指针 i 指向当前数字，内层循环指针 j 遍历 i 之后的所有数字。
        # 如果发现逆序对，即 state_list[i] > state_list[j]，累加器 inv_count 加 1。
        for i in range(len(state_list)):
            for j in range(i + 1, len(state_list)):
                if state_list[i] > state_list[j]:
                    inv_count += 1
        return inv_count

    start_inv = get_inversions(start_state)
    goal_inv = get_inversions(goal_state)
    # 奇偶性相同则可解
    return (start_inv % 2) == (goal_inv % 2)

# 2. 启发函数：曼哈顿距离
def manhattan_distance(state, goal_state):
    distance = 0
    for i in range(1, 9): # 遍历数字 1-8，忽略0
        # 找到数字 i 在当前状态和目标状态中的一维索引
        current_idx = state.index(i)
        goal_idx = goal_state.index(i)
        
        # 将一维索引转换为二维坐标 (row, col)
        curr_row, curr_col = current_idx // 3, current_idx % 3
        goal_row, goal_col = goal_idx // 3, goal_idx % 3
        
        # 累加曼哈顿距离：|x1 - x2| + |y1 - y2|
        distance += abs(curr_row - goal_row) + abs(curr_col - goal_col)
    return distance

# 3. 获取所有合法的下一步状态
def get_neighbors(node):
    neighbors =[]
    state = node.state
    zero_idx = state.index(0) # 找到空格(0)的位置
    row, col = zero_idx // 3, zero_idx % 3

    # 定义上、下、左、右移动的偏移量
    moves = {
        "Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1)
    }

    for action, (dr, dc) in moves.items():
        new_row, new_col = row + dr, col + dc
        # 检查移动后的新坐标是否还在 3x3 的棋盘范围内
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            # 将移动后的二维坐标重新转换为一维索引
            new_zero_idx = new_row * 3 + new_col
            
            # 由于当前状态(state)是元组(tuple)不可变，需先转为列表(list)才能修改元素
            new_state_list = list(state)
            
            # 在一维数组中交换 0(空格) 与目标位置数字的位置，完成状态转移
            new_state_list[zero_idx], new_state_list[new_zero_idx] = new_state_list[new_zero_idx], new_state_list[zero_idx]
            
            # 交换完成后，将新状态重新转换为元组(使其可哈希)，并加入到邻居节点列表中
            neighbors.append(tuple(new_state_list))
    return neighbors

# 4. A* 算法主函数
def a_star(start_state, goal_state):
    # 可解性提前拦截
    if not is_solvable(start_state, goal_state):
        print("初始状态与目标状态奇偶性不一致，此问题无解！")
        return None

    print("[系统] 问题可解，A* 算法开始搜索...\n")
    
    # 初始化起始节点
    start_node = Node(start_state, None, 0, manhattan_distance(start_state, goal_state))
    # 初始化open表
    open_list =[]
    heapq.heappush(open_list, start_node)
    # 初始化closed表，集合哈希表
    closed_set = set() # 存放已经探索过的状态 tuple
    
    max_open_length = 0 # 用于统计内存消耗
    # 主循环
    while open_list:
        max_open_length = max(max_open_length, len(open_list))
        
        # 取出 f 值最小的节点
        current_node = heapq.heappop(open_list)

        # 判断是否到达目标
        if current_node.state == goal_state:
            return current_node, len(closed_set), max_open_length

        # 加入闭表
        closed_set.add(current_node.state)

        # 扩展邻居节点
        for neighbor_state in get_neighbors(current_node):
            if neighbor_state in closed_set:
                continue
                
            g_new = current_node.g + 1
            h_new = manhattan_distance(neighbor_state, goal_state)
            neighbor_node = Node(neighbor_state, current_node, g_new, h_new)
            
            # 简单实现：不额外判断节点是否在open表中需要更新g值
            # 依靠 heapq 和 closed_set，稍微冗余但代码简洁高效
            heapq.heappush(open_list, neighbor_node)

    return None, len(closed_set), max_open_length

# 辅助打印函数
def print_path(goal_node):
    path =[]
    current = goal_node
    while current:
        path.append(current)
        current = current.parent
    path.reverse()
    
    for i, node in enumerate(path):
        print(f"--- [第 {i} 步] ---")
        print(f"g={node.g}, h={node.h}, f={node.f}")
        # 美化输出 3x3
        for r in range(3):
            row_str = " ".join(str(x) if x != 0 else " " for x in node.state[r*3 : r*3+3])
            print(f"[{row_str}]")
        print("")
    return len(path) - 1

# ================= 运行测试 =================
if __name__ == "__main__":
    # 使用 Tuple 表示一维状态
    START = (2, 8, 3, 1, 0, 4, 7, 6, 5)
    GOAL  = (1, 2, 3, 8, 0, 4, 7, 6, 5)

    print("初始状态:", START)
    print("目标状态:", GOAL)
    print("-" * 30)

    start_time = time.time()
    
    result_node, closed_size, max_open = a_star(START, GOAL)
    
    end_time = time.time()

    if result_node:
        steps = print_path(result_node)
        print("-" * 30)
        print(f"[统计信息]")
        print(f"寻找成功！最短步数: {steps} 步")
        print(f"算法扩展节点数 (Closed表大小): {closed_size} 个")
        print(f"最大生成节点数 (Open表峰值): {max_open} 个")
        print(f"运行时间: {end_time - start_time:.4f} 秒")