# 画两遍，先画地形，再画动物
from animal.animaltype import River


def print_board(board):
    board_blitz = [['_' for _ in range(7)]for _ in range(9)]
    for i in range(9):
        for j in range(7):
            ter = board.get_terrain([i, j])
            if ter:
                if isinstance(ter, River):
                    board_blitz[i][j] = ter.mark
                else:
                    name = ter.mark.split('_')
                    if name[0] == 'red':
                        board_blitz[i][j] = name[1][0]
                    else:
                        board_blitz[i][j] = name[1][0].upper()
    for i in range(9):
        for j in range(7):
            animal = board.get_animal([i, j])
            if animal:
                name = animal.name.split('_')
                if name[0] == 'red':
                    board_blitz[i][j] = name[1][0]
                else:
                    board_blitz[i][j] = name[1][0].upper()
    for line in board_blitz:
        print(line)


def print_animals(board):
    board_blitz = [['_' for _ in range(7)]for _ in range(9)]
    for i in range(9):
        for j in range(7):
            animal = board.get_animal([i, j])
            if animal:
                name = animal.name.split('_')
                if name[0] == 'red':
                    board_blitz[i][j] = name[1][0]
                else:
                    board_blitz[i][j] = name[1][0].upper()
    for line in board_blitz:
        print(line)
