import time
import os
import sys

# --- 迷宫定义 ---
# 0 表示空地，1 表示墙壁
MAZE = [
    [0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 1, 0, 0, 0],
    [1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0]
]

START = (0, 0)
GOAL = (4, 4)
ROWS = len(MAZE)
COLS = len(MAZE[0])

# --- 动画配置 ---
DELAY = 1  # 每步动画的延迟秒数

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_maze(current_path, current_node=None, threshold=0, status="正在探索..."):
    """
    可视化打印迷宫状态
    """
    clear_screen()
    print("=" * 30)
    print(f"🤖 IDA* 迷宫寻路可视化演示")
    print(f"💰 当前预算 (Threshold): {threshold}")
    print(f"📢 状态: {status}")
    print("=" * 30)
    
    for r in range(ROWS):
        row_str = ""
        for c in range(COLS):
            pos = (r, c)
            if pos == START:
                row_str += " S "  # 起点
            elif pos == GOAL:
                row_str += " G "  # 终点
            elif current_node and pos == current_node:
                row_str += " 🤠"  # 当前所在位置
            elif pos in current_path:
                row_str += " * "  # 已经走过的路径（红线）
            elif MAZE[r][c] == 1:
                row_str += "███"  # 墙壁
            else:
                row_str += " . "  # 空地
        print(row_str)
    print("=" * 30)
    print("图例: S=起点, G=终点, 🤠=当前位置, *=牵着的红线, ███=墙壁")
    time.sleep(DELAY)

def heuristic(pos):
    """曼哈顿距离作为启发式估值"""
    return abs(pos[0] - GOAL[0]) + abs(pos[1] - GOAL[1])

def get_neighbors(pos):
    """获取合法的邻居（不撞墙，不越界）"""
    r, c = pos
    neighbors = []
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]: # 上下左右
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and MAZE[nr][nc] == 0:
            neighbors.append((nr, nc))
    return neighbors

def ida_star_demo():
    """带有可视化的 IDA* 主逻辑"""
    threshold = heuristic(START)
    
    def search(node, g, current_path):
        f = g + heuristic(node)
        
        # 可视化：正在探索这个节点
        print_maze(current_path, node, threshold, f"计算花费 f={f} (g={g}+h={heuristic(node)})")
        
        # 剪枝判断
        if f > threshold:
            print_maze(current_path, node, threshold, f"❌ 超预算！预算:{threshold}, 花费:{f} -> 回头剪枝")
            time.sleep(DELAY * 2)
            return False, f
            
        if node == GOAL:
            print_maze(current_path, node, threshold, "✅ 找到终点了！")
            return True, node
            
        min_over_threshold = float('inf')
        
        for neighbor in get_neighbors(node):
            # 环路检测：不能踩到自己牵的红线上
            if neighbor in current_path:
                continue
                
            current_path.append(neighbor) # 放红线
            found, result = search(neighbor, g + 1, current_path)
            
            if found:
                return True, result
                
            if result < min_over_threshold:
                min_over_threshold = result
                
            current_path.pop() # 收红线 (回溯)
            
        return False, min_over_threshold

    # IDA* 的主循环：不断放大阈值
    while True:
        print_maze([], None, threshold, "🌀 开启新一轮探索...")
        time.sleep(DELAY * 2)
        
        path = [START]
        found, result = search(START, 0, path)
        
        if found:
            print("\n🎉 探索结束！最终的最短路径为:")
            print(" -> ".join([f"({r},{c})" for r, c in path]))
            break
            
        if result == float('inf'):
            print("\n😭 彻底走不通，无解！")
            break
            
        print_maze([], None, threshold, f"🔄 本轮探索失败，将预算从 {threshold} 提升至 {result}")
        time.sleep(DELAY * 3)
        threshold = result

if __name__ == "__main__":
    try:
        ida_star_demo()
    except KeyboardInterrupt:
        print("\n演示已手动终止。")
