from animal.animaltype import *
from animal.visualprint import print_board
import numpy as np
import animal.qiju.qiju as qj
import logging
logging.basicConfig(level=logging.INFO)


# 明棋
# 用图层的方式？还是用一个层呢，河、陷阱、塔是否要有个类呢，其对动物的特殊特殊性质是放在这些类里还是放在动物的类中呢
class Board:
    def __init__(self, qiju=qj.qiju2):
        animal_types = {'1': AnimalType.mouse, '2': AnimalType.cat, '3': AnimalType.dog, '4':AnimalType.wolf, '5': AnimalType.panther, '6':AnimalType.tiger, '7':AnimalType.lion, '8':AnimalType.elephant}
        if qiju is not None:
            # 格局残局生成棋盘
            self.grid = [[None for _ in range(7)] for _ in range(9)]
            for i in range(9):
                for j in range(7):
                    x = qiju[i][j]
                    if x == 0:
                        continue
                    team = Team.blue if x > 0 else Team.red
                    animaltype = animal_types[str(abs(x))]
                    self.grid[i][j] = AnimalFactory.produce_animal(animaltype, team)

        else:
            self.grid = [[None for _ in range(7)] for _ in range(3)]
            grid_down = [[None for _ in range(7)] for _ in range(3)]

            def composite_board(grid, team: Team):
                grid[0][0] = AnimalFactory.produce_animal(AnimalType.lion, team)
                grid[0][6] = AnimalFactory.produce_animal(AnimalType.tiger, team)
                grid[1][1] = AnimalFactory.produce_animal(AnimalType.dog, team)
                grid[1][5] = AnimalFactory.produce_animal(AnimalType.cat, team)
                grid[2][0] = AnimalFactory.produce_animal(AnimalType.mouse, team)
                grid[2][2] = AnimalFactory.produce_animal(AnimalType.panther, team)
                grid[2][4] = AnimalFactory.produce_animal(AnimalType.wolf, team)
                grid[2][6] = AnimalFactory.produce_animal(AnimalType.elephant, team)

            # 动物位置
            composite_board(self.grid, Team.red)
            composite_board(grid_down, Team.blue)
            self.grid.extend([[None for _ in range(7)] for _ in range(3)])
            for i in grid_down:
                i.reverse()
            self.grid.extend(grid_down[::-1])

        # 两种那个更好呢
        # 带地形的可以使用两层图层，一层动物，一层地形
        # self.grid = np.zeros((9, 7))    # 这个只能是数字，好像不能用呢

        self.terrain = [[None for _ in range(7)] for _ in range(3)]
        river = [[River() for _ in range(7)] for _ in range(3)]

        terrain_down = [[None for _ in range(7)] for _ in range(3)]
        self.possible_moves, self.possible_dicts = self.all_possible_moves()
        # 利用extend来拼接出棋盘，分成三个部分
        self.actionsize = len(self.possible_moves)

        # 地形构造
        def composite_terrian(grid, team: Team):
            grid[0][2] = Trap(team)
            grid[0][3] = Tower(team)
            grid[0][4] = Trap(team)
            grid[1][3] = Trap(team)
        composite_terrian(self.terrain, Team.red)
        composite_terrian(terrain_down, Team.blue)
        # 造河
        for i in river:
            i[0] = i[3] = i[6] = None
        self.terrain.extend(river)
        self.terrain.extend(terrain_down[::-1])

    def put(self, animal, location):
        self.grid[location[0]][location[1]] = animal
        # 在这里获得变换陷阱和河的变换

    def remove(self, location):
        self.grid[location[0]][location[1]] = None

    # 用于获得某个位置的动物
    def get_animal(self, location):
        return self.grid[location[0]][location[1]]

    def get_terrain(self, location):
        return self.terrain[location[0]][location[1]]

    @classmethod
    def strfboard(cls, board):
        result = ''
        for b in board:
            result += ''.join(str(i) for i in b)
        return result
        # todo 可以更近一步变成hash

    @classmethod
    def numberfy(cls, board):
        result = np.zeros((9, 7), dtype=int)
        for i in range(9):
            for j in range(7):
                animal = board[i][j]
                if animal:
                    if animal.team == Team.blue:
                        result[i][j] = animal.kind.value
                    else:
                        result[i][j] = -1 * animal.kind.value
        return result[:]

    @classmethod
    def turn_down(cls, board):
        """
        翻转数字棋盘
        :param board: 数字棋盘
        :return: 翻转后的数字棋盘
        """
        return np.flip(board)

    @classmethod
    def all_possible_moves(cls):
        moves1 = [[[2, y], [6, y]] for y in [1, 2, 4, 5]]
        moves1.extend([[move[1], move[0]] for move in moves1])
        moves2 = [[[x, 3], [x, y]] for y in [0, 6] for x in [3, 4, 5]]
        moves2.extend([[move[1], move[0]] for move in moves2])
        moves = []
        for i in range(9):
            for j in range(7):
                if i + 1 < 9:
                    moves.append([[i, j], [i+1, j]])
                if i - 1 >= 0:
                    moves.append([[i, j], [i-1, j]])
                if j + 1 < 7:
                    moves.append([[i, j], [i, j+1]])
                if j - 1 >= 0:
                    moves.append([[i, j], [i, j-1]])
        moves.extend(moves1)
        moves.extend(moves2)
        dicts = {}
        for index, possible in enumerate(moves):
            dicts[str(possible)] = index
        return moves, dicts

    def save_board(self):
        # 将棋局保存为文件，盖上时间戳，保存为一个字符串？
        board_blitz = [['0' for _ in range(7)] for _ in range(9)]
        for i in range(9):
            for j in range(7):
                animal = self.get_animal([i, j])
                if animal:
                    name = animal.name.split('_')
                    if name[0] == 'red':
                        board_blitz[i][j] = name[1][0]
                    else:
                        board_blitz[i][j] = name[1][0].upper()
        board_str = ''
        for line in board_blitz:
            for l in line:
                board_str += str(l)
        print(board_str)
        return board_str
        # 储存

    def load_board(self, str_board):
        # 将文件加载为棋局
        animal_types = {'m': AnimalType.mouse, 'c': AnimalType.cat, 'd': AnimalType.dog, 'w':AnimalType.wolf, 'p': AnimalType.panther, 't':AnimalType.tiger, 'l':AnimalType.lion, 'e':AnimalType.elephant}
        grid = [[None for _ in range(7)] for _ in range(9)]
        for index, s in enumerate(str_board):
            if s == '0':
                continue
            line = index//7
            colunm = index%7
            team = Team.red if ord(s) > 96 else Team.blue
            animal_type = animal_types[s.lower()]
            grid[line][colunm] = AnimalFactory.produce_animal(animal_type, team)
        self.grid = grid
        print('loading complete')


# 一个动作分成两个部分，一个是选中状态，一个是动作的发生地，如果是选中位置，则翻面，如果是周围位置，则移动或吃子
# 是否是合法动作 在哪里测试呢，应该是与gamestate相关。
class Move:
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos


def mirror_move(move):
    return [[8 - move[0][0], 6 - move[0][1]], [8 - move[1][0], 6 - move[1][1]]]


# 看围棋、象棋的源码 分析其写法
# 要实现每次apply_move后返回一个新的gamestate对象，这样可以更便于算法实现。成功。
class GameState:
    # no_effect_steps = 0

    def __init__(self, board, team, move, last_reset=None):
        self.board = board
        # todo team 要进行一个修改，直接在外面修改吧
        self.team = make_team(team)
        self.last_move = move
        self.last_reset = last_reset
        # reset就是用来检查是否存在有效步数的
        self.reset = False
        # 轨迹
        self.trajectory = []

    # 新游戏 玩家，玩家绑定的颜色，玩家的下棋顺序状态 玩家的选中状态
    @classmethod
    def new_game(cls, qiju=None):
        board = Board(qiju)
        team = Team.blue
        GameState.no_effect_steps = 0
        reset_river()
        return GameState(board, team, None, False)

    # 吃子
    def eat(self, move):
        start_animal = self.board.get_animal(move.start_pos)
        self.board.put(start_animal, move.end_pos)
        self.board.remove(move.start_pos)
        GameState.no_effect_steps = 0
        self.reset = True

    # 对子
    def neutralize(self, move):
        self.board.remove(move.end_pos)
        self.board.remove(move.start_pos)
        GameState.no_effect_steps = 0
        self.reset = True

    # 移动
    def moveaway(self, move):
        start_animal = self.board.get_animal(move.start_pos)
        self.board.put(start_animal, move.end_pos)
        self.board.remove(move.start_pos)

    # 走棋的方法 1 找到所有可以走的棋，放在一个列表了，有没翻的可以翻，翻的可以向四个方向中的几个走，2走棋 这时智能体的活
    # 对于这里的方法apply_move 1 判断能不能走 翻和运动两种，运动分移动，吃子和对子三种 2调用board里面的方法行动
    def apply_move(self, move):
        islegal, func = self.is_legal_move(move)
        if islegal:
            # 如果起点或终点是河，则调用mouse.get_into_river()
            # 如果起点或终点是trap，则调用animal.get_into_trap
            start, end = move.start_pos, move.end_pos
            if isinstance(self.board.get_terrain(start), River) or isinstance(self.board.get_terrain(end), River):
                self.board.get_animal(start).get_into_river(start, end)
            start_terrain = self.board.get_terrain(start)
            end_terrain = self.board.get_terrain(end)
            if isinstance(start_terrain, Trap) and start_terrain.team != self.team:
                self.board.get_animal(start).in_trap = False
            if isinstance(end_terrain, Trap) and end_terrain.team != self.team:
                self.board.get_animal(start).in_trap = True
            func(move)
            # 交换下棋方
            # GameState.no_effect_steps += 1
            # 检查
            self.trajectory.append(move)
            return True, GameState(self.board, self.team.other, move, self.reset)
        return islegal, self                                                                # 最完美的一步

    # 判断是否为合法的落子
    # 新问题：1老鼠能进水，但是不能再水里吃象，其他不能进水 2狮子和老虎能跳过水，移动或吃子，但是中间有老鼠不能
    #       3在对方trap中，对方任何动物都可以吃掉你，无论你是谁 4 到达对方tower就获得了胜利。
    # 2的实现方式：列举，但太多了 写一个函数 关键是在legal_moves中还得有体现
    # 可以在三个地方解决这个问题，gamestate类里 动物类，得给地形 地形类里，得知道布局
    # 如果把位置变成动物的属性呢？

    def is_legal_move(self, move):
        # 排除
        length_trajectory = len(self.trajectory)
        suspect1, suspect2 = None, None
        if length_trajectory >= 9:
            moves1 = self.trajectory[-9::2]
            suspect1 = self.is_legal_7_3(moves1)
        if length_trajectory >= 17:
            moves2 = self.trajectory[-33::2]
            suspect2 = self.is_legal_17_5(moves2)
        # 这里出现了不统一 需要改正 todo 有的是move有的是list
        start_pos = move.start_pos
        end_pos = move.end_pos

        # 若开始点或结束点在棋盘外，则不合法
        if not (0 <= start_pos[0] <= 8 and 0 <= start_pos[1] <= 6 and 0 <= end_pos[0] <= 8 and 0 <= end_pos[1] <= 6):
            return False, None

        start_animal = self.board.get_animal(start_pos)
        end_animal = self.board.get_animal(end_pos)
        # 我想到了一个绝妙的办法，把地形里的河放在初始化里

        # 若开始动物为空，则不合法
        # 若开始点为对方棋子，则不合法，
        if start_animal is None or start_animal.team != self.team:
            return False, None
        else:
            # 若开始点结束点间不能移动，则不合法
            if not start_animal.movable(start_pos, end_pos):
                return False, None
            else:
                # 若结束点为空，则合法，移动棋子
                if end_animal is None:
                    # if move[1] in suspect1 or move[1] in suspect2 and move[0] == self.trajectory[-1][1]:
                    #     return False, None
                    return True, self.moveaway
                # 若结束点为己方棋子，则不合法
                elif end_animal.team == self.team:
                    return False, None
                else:
                    # 若小，合法，吃子
                    if start_animal.eatable(end_animal):
                        return True, self.eat
                    # 若相等，合法，对子
                    elif start_animal.kind == end_animal.kind:
                        return True, self.neutralize
                    # 若对方棋子比己方棋子大，不合法
                    else:
                        return False, None

    # 记录某色棋所有合法的落子
    def legal_moves(self):
        moves = []
        locations = [[i, j] for i in range(9) for j in range(7)]
        for loc in locations:
            start_pos = loc
            animal = self.board.get_animal(start_pos)
            if not animal:    # 如果没有动物就跳过，这样也增加了效率
                continue
            end_poses_avail = [[loc[0]+1, loc[1]], [loc[0], loc[1]+1], [loc[0]-1, loc[1]], [loc[0], loc[1]-1]]
            end_poses = []
            for end_pos in end_poses_avail:
                if not (end_pos[0] > 8 or end_pos[0] < 0 or end_pos[1] > 6 or end_pos[1] < 0):
                    end_poses.append(end_pos)
            # 如果开始点是狮或虎，如果在河边，则加入河对岸的位置，但是这个在这里就拿到动物了，感觉太累赘了，不过好像还是这种方法容易实现一些
            if animal.kind == AnimalType.lion or animal.kind == AnimalType.tiger:
                for end_pos in end_poses:
                    if isinstance(self.board.get_terrain(end_pos), River):
                        end_poses.remove(end_pos)
                        # 从数组去掉这一个
                        if start_pos[0] - end_pos[0] == 0:                  # 同一排
                            dis = end_pos[1] - start_pos[1]
                            end_pos[1] += dis
                            while isinstance(self.board.get_terrain(end_pos), River):
                                end_pos[1] += dis
                        if start_pos[1] - end_pos[1] == 0:                  # 同一列
                            dis = end_pos[0] - start_pos[0]
                            end_pos[0] += dis
                            while isinstance(self.board.get_terrain(end_pos), River):
                                end_pos[0] += dis
                        end_poses.append(end_pos)

            # 还有一种方法，就是记录动物的位置，然后遍历动物，感觉这个更麻烦
            for end_pos in end_poses:
                move = Move(start_pos, end_pos)
                if self.is_legal_move(move)[0]:
                    moves.append(move)

        return moves
    # todo 添加规则 调试
    '''
    【7-3违例规则】：在连续7步棋内，如果同一动物连续超过3次进入同一棋格，在接下来的第8步棋将禁止该动物进入该棋格（若7步内有进入陷阱，则不受该限制；被追动物不受该限制）
    【17-5违例规则】：在连续17步棋内，如果只操作同一个动物，且该动物的活动范围不超过5个棋格，在接下来的第18步棋将禁止该动物进入上述5个棋格中的任意一个（若17步内有进入陷阱，则不受该限制）
    '''
    # 【7-3】1 是否是同一个棋子，检查连贯性。2是否包含陷阱。3 目的点是否有重复超过3次的。4.是否有被追逐。 是则排除重复3次的目的点
    # 【17-5】1 是否是同一个棋子，检查连贯性。2是否包含陷阱。3 目的点是否只包含以及少于5个棋格。是则排除重复这几个棋格。

    def is_legal_7_3(self, moves):
        # 检查是否为同一棋子
        for i in range(len(moves)-1):
            if moves[i][1] != moves[i][0]:
                return None
        # 检查是否包含陷阱
        for i in range(len(moves)):
            for j in range(2):
                if isinstance(self.board[moves[i][j][0]][moves[i][j][1]], Trap):
                    return None
        # 检查目的地是否超过3次
        directions = {}
        suspect = []
        for i in range(len(moves)):
            if directions[moves[i][1]]:
                directions[moves[i][1]] += 1
            else:
                directions[moves[i][1]] = 1
        for k, v in directions.items():
            if v >= 3:
                suspect.append(k)
        if len(suspect) == 0:
            return None
        # todo 检查是否被追逐 这里还挺麻烦的，还要考虑河和狮子老虎的问题
        animal = self.board[moves[0][0][0]][moves[0][0][1]]
        for i in range(1, len(moves)):
            move_origin = moves[i][0]
            if move_origin[0] + 1 < 9 and self.board[move_origin[0]+1][move_origin[1]].eatable(animal):
                return None
            if move_origin[0] - 1 >= 0 and self.board[move_origin[0]-1][move_origin[1]].eatable(animal):
                return None
            if move_origin[1] + 1 < 7 and self.board[move_origin[0]][move_origin[1]+1].eatable(animal):
                return None
            if move_origin[1] - 1 >= 0 and self.board[move_origin[0]+1][move_origin[1]-1].eatable(animal):
                return None
        return suspect

    def is_legal_17_5(self, moves):
        # 检查是否为同一棋子
        for i in range(len(moves)-1):
            if moves[i][1] != moves[i][0]:
                return None
        # 检查是否包含陷阱
        for i in range(len(moves)):
            for j in range(2):
                if isinstance(self.board[moves[i][j][0]][moves[i][j][1]], Trap):
                    return None
        # 检查目的地是否不超过5个
        suspect = []
        for i in range(len(moves)):
            suspect.append(moves[i][1])
        if len(suspect) > 5:
            return None
        return suspect

    # 平局的问题。需要一个计数器，每个回合计数器加1，当出现吃子，对子时，计数器归零。但计数器为70时，平局出现, 这个大概应该在Game里
    # 但又好像不行，得知道吃子或对子，应该联合起来解决。
    # 结束的情况，1另一方无棋可走，本方获胜 2一方到塔，本方获胜 3双方70步没有吃子，平局
    # 算对手没有棋还有一个办法，就是记录吃了哪些棋子，然后没有棋子就是输了
    # todo 还得判断最后一步是不是都没有棋子了若是，则平局 还得检验一下
    def get_winner(self):
        winner = None
        if not self.legal_moves():
            if (Board.numberfy(self.board.grid) == np.zeros((9, 7))).sum() == 63:
                return True, None
            else:
                print(self.team)
                winner = self.team.value * -1
                return True, winner
        else:
            animal1 = self.board.get_animal([0, 3])
            if animal1 and animal1.team == Team.blue:
                winner = Team.blue.value
            animal2 = self.board.get_animal([8, 3])
            if animal2 and animal2.team == Team.red:
                winner = Team.red.value
        if winner:
            return True, winner
        else:
            # if GameState.no_effect_steps > 70:
            #     return True, None
            # else:
            return False, None


# 以棋盘为核心的架构，比如围棋、五子棋，黑白棋，他的棋子都是相同地位的
# 还是以棋子为核心的架构，比如象棋，国际象棋，每个棋子都有自己的特殊走法
# 兽棋明棋中，鼠，狮，虎有不同的走法，狮虎走法相同。因此两种构建方法都是可行的，这里我决定先使用以棋盘为核心的架构

class AGame:
    def __init__(self, firstAgent, secondAgent):
        self.isgameover = True
        self.firstAgent = firstAgent
        self.secondAgent = secondAgent
        self.gamestate = None
        self.startGame()
        self.isgameover = True
        self.count = 0

    def startGame(self):
        while True:
            if self.isgameover:
                key = input("press any key to start")
                if key == 'q':
                    return
                self.gamestate = GameState.new_game()
                print_board(self.gamestate.board)
                self.isgameover = False
            # 第一个人下棋的部分
            while not self.isgameover:
                islegal, self.gamestate = self.gamestate.apply_move(self.firstAgent.makeMove(self.gamestate))
                if islegal:
                    print_board(self.gamestate.board)
                    self.check_winner(self.gamestate)
                    break
            # 第二个Agent下棋的部分
            while not self.isgameover:
                islegal, self.gamestate = self.gamestate.apply_move(self.secondAgent.makeMove(self.gamestate))
                if islegal:
                    print_board(self.gamestate.board)
                    self.check_winner(self.gamestate)
                    break

    def check_winner(self, gamestate):
        is_over, winner = gamestate.get_winner()
        if is_over:
            self.isgameover = True
            print("winner is {}".format(winner))
            return True
        elif self.count > 70:
            print("it's a draw")
            return True
        else:
            if gamestate.reset:
                self.count = 0
            else:
                self.count += 1
            return False


if __name__ == "__main__":
    gs = GameState.new_game()
    print(Board.numberfy(gs.board.grid))
    gs.board.save_board()
    str_board = 'l0000000d000c0m0p0w0e000000000000000000000E0W0P0M0C000D0T00000l'
    gs.board.load_board(str_board)
    print(Board.numberfy(gs.board.grid))
    # 1遍历, 这是肯定能解决的办法，2对称法，让all_possible_moves对称的，可以直接算，best，3还有就是字符串字典，然后直接倒过来，直接查了。4

# todo 1构建由残局生成的游戏，2构建残局
