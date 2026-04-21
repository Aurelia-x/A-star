import sys
import time

# 预留导入，后续等 B 同学和 A 同学完成模块后取消注释
# from domains import PuzzleProblem, MazeProblem
# from heuristics import h_manhattan, h_linear_conflict
# from algorithms import a_star, bfs, dijkstra, ida_star

def print_board(state, dimension):
    """
    辅助函数：将一维状态美观地打印成二维棋盘
    """
    for i in range(0, len(state), dimension):
        row = state[i:i+dimension]
        # 把 0 替换为空白，更像真实的拼图
        print(" ".join(f"{str(x):>2}" if x != 0 else "  " for x in row))
    print("-" * (dimension * 3))

def main():
    print("="*50)
    print("🤖 欢迎来到启发式搜索算法演示系统 🤖")
    print("="*50)
    
    # --- 1. 用户交互：选择问题 ---
    print("\n[1/3] 请选择要解决的问题模型：")
    print("  1. 8数码问题 (3x3 经典难度)")
    print("  2. 15数码问题 (4x4 噩梦难度)")
    print("  3. 二维迷宫寻路 (扩展演示)")
    
    prob_choice = input("请输入选项 (1/2/3): ").strip()
    
    # --- 2. 用户交互：选择算法 ---
    print("\n[2/3] 请选择核心搜索算法：")
    print("  1. A* 算法 (标准最优解)")
    print("  2. BFS 广度优先搜索 (无启发盲搜)")
    print("  3. Dijkstra 算法 (基于代价盲搜)")
    print("  4. IDA* 算法 (极限省内存)")
    print("  5. 加权 A* (W=2.0 贪心极速次优解)")
    
    algo_choice = input("请输入选项 (1/2/3/4/5): ").strip()
    
    # --- 3. 用户交互：选择启发函数 (如果需要) ---
    heuristic_choice = "1"
    if algo_choice in ["1", "4", "5"]:
        print("\n[3/3] 该算法需要启发函数(Heuristic)，请选择：")
        print("  1. 曼哈顿距离 (经典)")
        print("  2. 曼哈顿 + 线性冲突 (极致剪枝)")
        print("  3. 错位棋子数 (较弱启发)")
        heuristic_choice = input("请输入选项 (1/2/3): ").strip()
        
    print("\n" + "="*50)
    print("🛠️  正在拼装您的选择组合，开始运行...")
    print("="*50)
    
    # TODO: 核心组装与运行逻辑 (等待模块开发完毕后填入)
    # 以下为逻辑演示占位符：
    # problem = PuzzleProblem(dimension=3) if prob_choice == "1" else ...
    # heuristic = h_manhattan if heuristic_choice == "1" else ...
    # if algo_choice == "1":
    #     path_actions, path_states, expanded, max_open, t_cost = a_star(problem, heuristic)
    
    # 模拟系统思考和输出过程...
    time.sleep(1.5)
    print("\n✅ 搜索完成！(以下为模拟输出)")
    print(f"⏱️ 耗时: 0.1234 秒")
    print(f"🧠 扩展节点数 (Closed表大小): 1560")
    print(f"📦 内存峰值 (Open表大小): 850")
    print(f"🏁 找到的最优路径步数: 12 步")
    print(f"🗺️ 动作序列: Up -> Left -> Down -> Right ...")
    
    # TODO: 后续在这里循环打印 path_states 数组，演示完整的走棋动画
    print("\n[演示完毕] 如果您想查看大数据跑批结果，请运行 benchmark.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已手动终止。")
        sys.exit(0)
