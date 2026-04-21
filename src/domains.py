import random
from base_classes import BaseProblem


class PuzzleProblem(BaseProblem):
    """
    数码问题（8数码 / 15数码）的具体实现。
    dimension=3 → 8数码 (3×3)
    dimension=4 → 15数码 (4×4)
    状态用一维 tuple 表示，0 代表空格。
    """

    def __init__(self, dimension, start, goal):
        """
        dimension : int  — 棋盘边长，3 或 4
        start     : tuple — 初始状态，如 (2,8,3,1,0,4,7,6,5)
        goal      : tuple — 目标状态，如 (1,2,3,8,0,4,7,6,5)
        """
        self.dimension = dimension
        self.start = tuple(start)
        self.goal = tuple(goal)

    def get_start_state(self):
        return self.start

    def get_goal_state(self):
        return self.goal

    def is_goal(self, state):
        return state == self.goal

    def get_successors(self, state):
        successors = []
        d = self.dimension

        zero_idx = state.index(0)
        zero_row = zero_idx // d
        zero_col = zero_idx % d

        directions = [
            ("Up",    -1,  0),
            ("Down",   1,  0),
            ("Left",   0, -1),
            ("Right",  0,  1),
        ]

        for action, dr, dc in directions:
            new_row = zero_row + dr
            new_col = zero_col + dc

            if not (0 <= new_row < d and 0 <= new_col < d):
                continue

            new_idx = new_row * d + new_col

            new_state = list(state)
            new_state[zero_idx], new_state[new_idx] = \
                new_state[new_idx], new_state[zero_idx]

            successors.append((action, tuple(new_state), 1))

        return successors

    def is_solvable(self):
        def get_inversions(state):
            flat = [x for x in state if x != 0]
            inversions = 0
            for i in range(len(flat)):
                for j in range(i + 1, len(flat)):
                    if flat[i] > flat[j]:
                        inversions += 1
            return inversions

        inv_start = get_inversions(self.start)
        inv_goal = get_inversions(self.goal)

        if self.dimension % 2 != 0:
            # 奇数维度（如 3x3 8数码）：初始状态与目标状态的逆序数奇偶性必须一致
            return (inv_start % 2) == (inv_goal % 2)
        else:
            # 偶数维度（如 4x4 15数码）：
            # 逆序数奇偶性 + 空格离底部的行数 的奇偶性 必须与目标状态一致
            start_zero_row = self.start.index(0) // self.dimension
            goal_zero_row = self.goal.index(0) // self.dimension
            
            start_dist = (self.dimension - 1) - start_zero_row
            goal_dist = (self.dimension - 1) - goal_zero_row
            
            return ((inv_start + start_dist) % 2) == ((inv_goal + goal_dist) % 2)

    def print_state(self, state):
        d = self.dimension
        print("+" + "---+" * d)
        for row in range(d):
            row_str = "|"
            for col in range(d):
                val = state[row * d + col]
                row_str += f" {val if val != 0 else ' '} |"
            print(row_str)
            print("+" + "---+" * d)


# ====================================================================== #
#  迷宫寻路问题（0=路，1=墙）
# ====================================================================== #

class MazeProblem(BaseProblem):
    """
    二维网格迷宫寻路。
    grid : 二维列表，0 = 路（可通行），1 = 墙（不可通行）
    start_pos / goal_pos : (row, col) 元组。
    """

    def __init__(self, grid, start_pos, goal_pos):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.start_pos = tuple(start_pos)
        self.goal_pos = tuple(goal_pos)

    @classmethod
    def generate_random_maze(cls, rows, cols, obstacle_ratio=0.3, max_weight=1, seed=None):
        """
        生成一个随机迷宫。
        obstacle_ratio: 墙壁(值为1)的比例
        max_weight: 如果大于 1，则迷宫的空地上会随机出现代价为 [2, max_weight] 的“泥潭”。
        """
        if seed is not None:
            random.seed(seed)
            
        grid = [[0 for _ in range(cols)] for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                if (r, c) == (0, 0) or (r, c) == (rows - 1, cols - 1):
                    continue  # 起点和终点绝对不能是墙
                if random.random() < obstacle_ratio:
                    grid[r][c] = 1
                elif max_weight > 1:
                    # 有 20% 的概率在这块平地上生成一个泥潭
                    if random.random() < 0.2:
                        grid[r][c] = random.randint(2, max_weight)
                    
        return cls(grid, (0, 0), (rows - 1, cols - 1))

    def get_start_state(self):
        return self.start_pos

    def get_goal_state(self):
        return self.goal_pos

    def is_goal(self, state):
        return state == self.goal_pos

    def get_successors(self, state):
        successors = []
        row, col = state

        directions = [
            ("Up",    -1,  0),
            ("Down",   1,  0),
            ("Left",   0, -1),
            ("Right",  0,  1),
        ]

        for action, dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            if not (0 <= new_row < self.rows and 0 <= new_col < self.cols):
                continue

            cell_val = self.grid[new_row][new_col]
            if cell_val != 1:  # 1 代表墙壁，不可通行
                # 变长边权：如果格子的值是 0，代价为 1（平地）
                # 如果格子的值大于 1，则代表泥潭/减速带，代价就是该值
                cost = cell_val if cell_val > 1 else 1
                successors.append((action, (new_row, new_col), cost))

        return successors

    def is_solvable(self):
        r0, c0 = self.start_pos
        rg, cg = self.goal_pos
        # 起点终点必须都在路上（0）
        if self.grid[r0][c0] == 1 or self.grid[rg][cg] == 1:
            return False
            
        # 使用快速的内部 BFS 检查连通性
        # 这是一个极简版的广度优先搜索，它的唯一目的是回答“起点能不能连通到终点？”
        # 相比 algorithms.py 中的完整版，它做了极大的“减法”：
        # 1. 零对象创建：直接使用坐标元组 (row, col)，不实例化沉重的 Node 对象
        # 2. 不记来时路：不保存 parent 指针，不需要重建路径
        # 3. 极简判断：只要能走到目标点立刻返回 True
        visited = set()
        from collections import deque
        queue = deque([self.start_pos])
        visited.add(self.start_pos)
        
        while queue:
            curr = queue.popleft()
            if curr == self.goal_pos:
                return True
                
            for _, next_pos, _ in self.get_successors(curr):
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append(next_pos)
                    
        return False

    def print_maze(self, path_states=None):
        """打印迷宫（S=起点, G=终点, 1=墙, 0=路）"""
        path_set = set(path_states) if path_states else set()
        for r in range(self.rows):
            row_str = ""
            for c in range(self.cols):
                pos = (r, c)
                if pos == self.start_pos:
                    row_str += "S "
                elif pos == self.goal_pos:
                    row_str += "G "
                elif pos in path_set:
                    row_str += "* "
                elif self.grid[r][c] == 1:  # 1是墙
                    row_str += "1 "
                else:  # 0是路
                    row_str += "0 "
            print(row_str)