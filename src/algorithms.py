import time
import heapq
from collections import deque
from base_classes import Node
from heuristics import h_zero

def reconstruct_path(node):
    """
    辅助函数：从目标节点回溯到初始节点，生成动作序列和状态序列。
    通过 parent 指针链逐级向上回溯，最后反转得到"起点→终点"的顺序。
    """
    path_actions = []
    path_states = []
    current = node
    while current:
        path_states.append(current.state)        # 收集状态
        if current.action is not None:
            path_actions.append(current.action)   # 收集动作
        current = current.parent                  # 沿 parent 链回溯
    return path_actions[::-1], path_states[::-1]  # 反转得到正向序列

def bfs(problem):
    """
    广度优先搜索 (BFS)
    不使用启发式函数，按层级扩展节点。适用于边权为1的最短路径问题。
    极易发生组合爆炸，通常用于作为算法性能对比的“垫底”基准。
    """
    start_time = time.perf_counter()
    start_state = problem.get_start_state()
    
    if not problem.is_solvable():
        return [], [], 0, 0, time.perf_counter() - start_time, 0
        
    start_node = Node(start_state, None, 0, 0, None)
    
    # BFS 使用双端队列作为 Frontier (Open表)
    queue = deque([start_node])
    closed_set = set()
    
    nodes_expanded = 0
    max_open_size = 0
    
    # BFS 主循环：按层级逐层扩展
    while queue:
        max_open_size = max(max_open_size, len(queue))
        current_node = queue.popleft()  # FIFO：先入先出，保证按层遍历
        
        if problem.is_goal(current_node.state):
            path_actions, path_states = reconstruct_path(current_node)
            time_cost = time.perf_counter() - start_time
            # 返回值：(动作序列, 状态序列, 扩展节点数, 内存峰值[Open表最大长度], 耗时, 总代价)
            return path_actions, path_states, nodes_expanded, max_open_size, time_cost, current_node.g

        # 已访问检测：跳过已在闭表中的状态
        if current_node.state in closed_set:
            continue
            
        closed_set.add(current_node.state)
        nodes_expanded += 1
        
        # 扩展后继节点：BFS 使用队列尾追加，保证 FIFO 顺序
        for action, next_state, cost in problem.get_successors(current_node.state):
            if next_state not in closed_set:
                neighbor_node = Node(next_state, current_node, current_node.g + cost, 0, action)
                queue.append(neighbor_node)
                
    return [], [], nodes_expanded, max_open_size, time.perf_counter() - start_time, 0

def dijkstra(problem):
    """
    Dijkstra 算法
    实质上是 f = g + h 中，强制令 h = 0 的 A* 算法变体。
    它会盲目地向所有方向扩展代价最小的节点。
    """
    # Dijkstra 就是 h 恒为 0 的 A*，直接复用 A* 逻辑即可
    return a_star(problem, h_zero, weight=1.0)

def a_star(problem, heuristic_func, weight=1.0):
    """
    A* 算法核心框架
    :param problem: 实现了 BaseProblem 接口的问题实例
    :param heuristic_func: 启发式函数，接收 (state, goal_state) 返回预估代价 h
    :param weight: 启发函数的权重。当 weight > 1.0 时演变为加权 A*（贪心寻路）
    """
    start_time = time.perf_counter()
    start_state = problem.get_start_state()
    
    # 尝试获取目标状态用于启发式计算，如果问题没有显式的单一目标状态，则返回 None
    goal_state = getattr(problem, 'get_goal_state', lambda: None)()
    
    if not getattr(problem, 'is_solvable', lambda: True)():
        return [], [], 0, 0, time.perf_counter() - start_time, 0
        
    # 计算初始节点的 h 和 f 值
    # f = g + w*h，其中 w=weight 控制启发式的"贪婪程度"
    h_start = heuristic_func(start_state, goal_state)
    start_node = Node(start_state, None, 0, h_start * weight, None)
    
    # Open 表：最小堆，按 f 值排序
    open_list = []
    heapq.heappush(open_list, start_node)
    # Closed 表：记录已扩展过的状态，防止重复
    closed_set = set()
    
    nodes_expanded = 0
    max_open_size = 0
    
    while open_list:
        max_open_size = max(max_open_size, len(open_list))
        current_node = heapq.heappop(open_list)  # 取出 f 值最小的节点
        
        # 延迟删除：弹出节点若已在闭表中，说明是旧副本，跳过
        if current_node.state in closed_set:
            continue
            
        if problem.is_goal(current_node.state):
            path_actions, path_states = reconstruct_path(current_node)
            time_cost = time.perf_counter() - start_time
            # 返回值：(动作序列, 状态序列, 扩展节点数, 内存峰值[Open表最大长度], 耗时, 总代价)
            return path_actions, path_states, nodes_expanded, max_open_size, time_cost, current_node.g

        # 将当前节点标为已扩展，加入闭表
        closed_set.add(current_node.state)
        nodes_expanded += 1
        
        # 扩展后继：为每个合法动作生成新状态
        for action, next_state, cost in problem.get_successors(current_node.state):
            if next_state in closed_set:
                continue
                
            g_new = current_node.g + cost          # 实际累积代价
            h_new = heuristic_func(next_state, goal_state)  # 启发式估值
            # 加权 f 值：w>1 时偏向贪心，w=1 时保证最优
            f_new = g_new + weight * h_new 
            
            # 创建新节点并压入优先队列（简单实现策略：允许重复节点进入堆）
            neighbor_node = Node(next_state, current_node, g_new, weight * h_new, action)
            # 强制覆盖 f 属性以适应加权
            neighbor_node.f = f_new 
            
            heapq.heappush(open_list, neighbor_node)

    # 搜索失败：Open 表为空仍未找到目标
    return [], [], nodes_expanded, max_open_size, time.perf_counter() - start_time, 0

def ida_star(problem, heuristic_func):
    """
    迭代加深 A* 算法 (IDA*)
    结合了 DFS 的空间效率和 A* 的启发式剪枝。
    极其节省内存，是解决 15 数码等高维问题的杀手锏。
    """
    start_time = time.perf_counter()
    start_state = problem.get_start_state()
    goal_state = getattr(problem, 'get_goal_state', lambda: None)()
    
    if not getattr(problem, 'is_solvable', lambda: True)():
        return [], [], 0, 0, time.perf_counter() - start_time, 0

    # 初始阈值为初始状态的启发值
    threshold = heuristic_func(start_state, goal_state)
    start_node = Node(start_state, None, 0, threshold, None)
    
    # 统计数据使用列表封装，以便在递归内部修改
    stats = {'nodes_expanded': 0}
    
    def search(node, g, current_threshold, current_path_states):
        """
        带有深度限制的递归深度优先搜索（DFS）
        只在 f <= threshold 的范围内探索，超过阈值则剪枝并返回该分支的最小超限值。
        返回: (是否找到目标, 新的阈值 或 目标节点)
        """
        f = g + heuristic_func(node.state, goal_state)
        
        # 如果当前 f 值超过了阈值，剪枝并返回当前 f 作为下一次的参考阈值
        if f > current_threshold:
            return False, f
            
        if problem.is_goal(node.state):
            return True, node
            
        stats['nodes_expanded'] += 1
        # 记录本轮探索中超过阈值的最小 f 值，作为下一轮的新阈值
        min_over_threshold = float('inf')
        
        for action, next_state, cost in problem.get_successors(node.state):
            # 环路检测：防止在当前 DFS 路径上反复横跳
            if next_state in current_path_states:
                continue
                
            current_path_states.add(next_state)
            next_node = Node(next_state, node, g + cost, heuristic_func(next_state, goal_state), action)
            
            found, result = search(next_node, g + cost, current_threshold, current_path_states)
            
            if found:
                return True, result
            # result 此时是超限分支的最小 f 值，用于更新下一轮阈值
            if result < min_over_threshold:
                min_over_threshold = result
                
            current_path_states.remove(next_state)  # 回溯：恢复路径状态
            
        return False, min_over_threshold

    # IDA* 的主循环：每轮用新阈值完整搜索一次
    # 阈值从初始启发值开始，每轮取上一轮统计的最小超限 f 值
    while True:
        # 每次从头开始搜索，但带有环路检测的集合
        path_set = {start_state}
        found, result = search(start_node, 0, threshold, path_set)
        
        if found:
            # result 此时是目标 node
            path_actions, path_states = reconstruct_path(result)
            time_cost = time.perf_counter() - start_time
            # IDA* 不维护 Open 表，max_open_size 记为路径最大深度
            # 返回值：(动作序列, 状态序列, 扩展节点数, 路径深度[替代Open], 耗时, 总代价)
            return path_actions, path_states, stats['nodes_expanded'], len(path_actions), time_cost, result.g
            
        if result == float('inf'):
            # 整个状态空间都搜完了，仍然没找到（问题无解或阈值已覆盖全部可能）
            break
            
        # 关键：确保新阈值严格大于旧阈值，防止浮点精度或启发式不足导致的死循环
        if result <= threshold:
            threshold += 1
        else:
            threshold = result

    # 搜索失败：所有阈值迭代完成仍未找到目标
    return [], [], stats['nodes_expanded'], 0, time.perf_counter() - start_time, 0
