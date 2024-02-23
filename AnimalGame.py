from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
import numpy as np
from animal import animal_chess
from animal.visualprint import print_board


class AnimalGame(Game):
    def __init__(self, n):
        self.board = animal_chess.Board()
        self.all_possible_action, self.action_dict = self.board.all_possible_moves()

    def getInitBoard(self):
        # return initial board (numpy board)
        b = self.board
        return np.array(animal_chess.Board.numberfy((b.grid)))

    def getBoardSize(self):
        # (a,b) tuple
        return (7, 9)

    def getActionSize(self):
        # return number of actions
        return self.board.actionsize

    def getNextState(self, grid, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        # 这段代码有两个问题，1 board的问题如何处理，本人是采用gamestate的方法。
        # 2 存在天然的不统一，兽棋中的一个动作包括出发地和目的地两个位置，而ttt棋只包括一个位置
        # 但是我们已经实现了一个all_possible_moves的东西，可以通过哪个来实现统一
        grid_cp = np.copy(grid)
        self.board = animal_chess.Board(qiju=grid_cp)
        gs = animal_chess.GameState(board=self.board, team=player, move=action)
        # todo 这里有待解决的问题，action源代码是上一步的，action的格式也不准确，需要切换一下
        # 这里的上一步主要是为了7-3规则等要素
        # 这里需要将action转换一下
        # todo 那个mirroaction不知道这里是怎么实现的，有可能有问题
        # todo 一直是一边移动 这里存在问题，那一开始是下边动了一下，后面就全是上面动了，肯定存在混乱
        ########################################
        move = self.all_possible_action[action]
        # todo to be check
        if player == -1 or (isinstance(player, animal_chess.Team) and player.value == -1):
            move = animal_chess.mirror_move(move)
        move = animal_chess.Move(move[0], move[1])
        is_legal, next_gs = gs.apply_move(move=move)
        if is_legal:
            return (animal_chess.Board.numberfy(next_gs.board.grid), next_gs.team)
        else:
            # todo 总是到这里，或许action 搞错了
            # float division by zero
            print("wrong aciton applied")
            return grid, player

    def getValidMoves(self, grid, player):
        # return a fixed size binary vector
        # 是不是要使用到copy呢， 就用吧
        grid_cp = np.copy(grid)
        self.board = animal_chess.Board(qiju=grid_cp)
        gs = animal_chess.GameState(board=self.board, team=player, move=None)
        moves = gs.legal_moves()
        # 要做转换
        actions = np.zeros(len(self.all_possible_action))
        for move in moves:
            key = str([move.start_pos, move.end_pos])
            action = self.action_dict[key]
            actions[action] = 1
        # 这里应该返回numpy 全部的onehot标签
        return actions
        # todo 论文 这里有一个可以写到论文里面的内容，就是现在系统给出的是代表Move的序列，并不能反映Move的空间位置
        # todo 所以应该怎样才能体现这种空间位置呢，可以去借鉴象棋或者国际象棋的方法。
        # 这个是不是不用呢，还是需要的。
        # valids = [0]*self.getActionSize()
        # b = Board(self.n)
        # b.pieces = np.copy(board)
        # legalMoves =  b.get_legal_moves(player)
        # if len(legalMoves)==0:
        #     valids[-1]=1
        #     return np.array(valids)
        # for x, y in legalMoves:
        #     valids[self.n*x+y]=1
        # return np.array(valids)

    def getGameEnded(self, grid, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        # todo 要不要标准化
        grid_cp = np.copy(grid)
        self.board = animal_chess.Board(qiju=grid_cp)
        gs = animal_chess.GameState(board=self.board, team=player, move=None)
        is_end, winner = gs.get_winner()
        if is_end:
            if winner == 0:
                return 1e-4
            else:
                return winner
        else:
            return 0
        # b = Board(self.n)
        # b.pieces = np.copy(board)
        # if b.has_legal_moves(player):
        #     return 0
        # if b.has_legal_moves(-player):
        #     return 0
        # if b.countDiff(player) > 0:
        #     return 1
        # return -1
        # draw has a very little value

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        # TypeError: can't multiply sequence by non-int of type 'Team'
        # todo 需要翻转
        if player == -1 or player == 1:
            if player == -1:
                r = player * board
                r = r[::-1, ::-1]
            else:
                r = board
        else:
            if player.value == -1:
                r = player.value * board
                r = r[::-1, ::-1]
            else:
                r = board
        return r

    def getSymmetries(self, board, pi):
        # mirror, rotational 镜像、旋转
        # 对于兽棋智能翻转，不能镜像和旋转，所以这里返回None? todo 好像应该返回点儿什么
        return [(board, pi)]

        # assert(len(pi) == self.n**2+1)  # 1 for pass
        # pi_board = np.reshape(pi[:-1], (self.n, self.n))
        # l = []
        #
        # for i in range(1, 5):
        #     for j in [True, False]:
        #         newB = np.rot90(board, i)
        #         newPi = np.rot90(pi_board, i)
        #         if j:
        #             newB = np.fliplr(newB)
        #             newPi = np.fliplr(newPi)
        #         l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        # return l

    def stringRepresentation(self, grid):
        b_str = animal_chess.Board.strfboard(grid)
        return b_str

    @staticmethod
    def display(grid):
        b = animal_chess.Board(grid)
        print("\n")
        print_board(b)


#  这也是一个问题 maximum recursion depth exceeded while calling a Python object