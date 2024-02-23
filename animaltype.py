import enum


def make_river():
    river_map = [[0] * 7] * 3
    mid = [[0, 1, 1, 0, 1, 1, 0] for _ in range(3)]
    river_map.extend(mid)
    river_map.extend([[0] * 7] * 3)
    return river_map


# class Team(enum.Enum):
#     blue = 1
#     red = -1
#
#     @property
#     def other(self):
#         return Team.blue if self == Team.red else Team.red
#
#     @property
#     def value(self):
#         return 1 if self == Team.blue else -1
#
#
# def make_team(value):
#     if value == 1:
#         return Team.blue
#     elif value == -1:
#         return Team.red
#     else:
#         return value


class AnimalType(enum.Enum):
    mouse = 1
    cat = 2
    dog = 3
    wolf = 4
    panther = 5
    tiger = 6
    lion = 7
    elephant = 8
    common = 9


# todo 太笨了，这个，回头要好好改一下，现在的问题是重玩的时候，得restore一下。
river = make_river()


# 根本没有river这一项？ todo 这里可能有问题
def reset_river():
    global river
    river = make_river()


class Animal:
    def __int__(self, team):
        self.kind = AnimalType.common
        self.team = team
        self.in_trap = False

    def eatable(self, otheranimal):
        if otheranimal.in_trap and otheranimal.team != self.team:
            return True
        if self.team != otheranimal.team and self.kind.value > otheranimal.kind.value:
            return True
        return False

    # 是否可移动 一般如果是河不能移动
    def movable(self, start, end):
        if river[end[0]][end[1]] == 0 and ((start[0] == end[0] and abs(start[1] - end[1]) == 1) or (start[1] == end[1] and abs(start[0] - end[0]) == 1)):
            return True
        return False


# 工厂模式 三种工厂模式中的简单工厂模式
class AnimalFactory:
    @staticmethod
    def produce_animal(animaltype, team):
        if animaltype == AnimalType.mouse:
            return Mouse(team)
        elif animaltype == AnimalType.cat:
            return Cat(team)
        elif animaltype == AnimalType.dog:
            return Dog(team)
        elif animaltype == AnimalType.wolf:
            return Wolf(team)
        elif animaltype == AnimalType.panther:
            return Panther(team)
        elif animaltype == AnimalType.tiger:
            return Tiger(team)
        elif animaltype == AnimalType.lion:
            return Lion(team)
        elif animaltype == AnimalType.elephant:
            return Elephant(team)
        else:
            return -1


class Mouse(Animal):
    def __init__(self, team):
        self.in_trap = False
        self.team = team
        self.kind = AnimalType.mouse
        self.name = team.__str__().split('.')[1] + "_mouse"
        self.is_in_water = False

    # 比较棋子大小
    def eatable(self, otheranimal):
        # 如果是对方大象，并且自己不在水里可以吃
        # 如果对方在自己的陷阱里，可以吃
        if otheranimal.kind == AnimalType.elephant and otheranimal.team != self.team and not self.is_in_water:
            return True
        if otheranimal.in_trap and otheranimal.team != self.team:
            return True
        return False

    # 如果是岸到河 河变2
    # 河到河 start变1 end变2
    # 河到岸 start变1
    def get_into_river(self, start, end):
        if river[start[0]][start[1]] == 0:          # 从岸到河
            river[end[0]][end[1]] = 2
            self.is_in_water = True
        else:                                       # 起点是河
            if river[end[0]][end[1]] == 1:          # 河到河
                river[start[0]][start[1]] = 1
                river[end[0]][end[1]] = 2
            else:                                   # 起点是河，终点是岸
                river[start[0]][start[1]] = 1
                self.is_in_water = False

    def movable(self, start, end):
        if (start[0] == end[0] and abs(start[1] - end[1]) == 1) or (start[1] == end[1] and abs(start[0] - end[0]) == 1):
            return True
        return False


class Cat(Animal):
    def __init__(self, team):
        self.in_trap = False
        self.kind = AnimalType.cat
        self.team = team
        self.name = team.__str__().split('.')[1] + "_cat"


class Dog(Animal):
    def __init__(self, team):
        self.in_trap = False
        self.kind = AnimalType.dog
        self.team = team
        self.name = team.__str__().split('.')[1] + "_dog"


class Wolf(Animal):
    def __init__(self, team):
        self.in_trap = False
        self.kind = AnimalType.wolf
        self.team = team
        self.name = team.__str__().split('.')[1] + "_wolf"


class Panther(Animal):
    def __init__(self, team):
        self.in_trap = False
        self.kind = AnimalType.panther
        self.team = team
        self.name = team.__str__().split('.')[1] + "_panther"


class Tiger(Animal):
    def __init__(self, team):
        self.in_trap = False
        self.kind = AnimalType.tiger
        self.team = team
        self.name = team.__str__().split('.')[1] + "_tiger"

    def movable(self, start, end):
        if river[end[0]][end[1]] == 0 and ((start[0] == end[0] and abs(start[1] - end[1]) == 1) or (start[1] == end[1] and abs(start[0] - end[0]) == 1)):
            return True
        if start[0] == end[0]:
            bigger = max(start[1], end[1])
            smaller = min(start[1], end[1])
            if bigger - smaller == 1:
                return False
            for i in range(smaller+1, bigger):
                if river[start[0]][i] != 1:
                    return False
            return True
        if start[1] == end[1]:
            bigger = max(start[0], end[0])
            smaller = min(start[0], end[0])
            if bigger - smaller == 1:
                return False
            for i in range(smaller+1, bigger):
                if river[i][start[1]] != 1:
                    return False
            return True
        return False


class Lion(Animal):
    def __init__(self, team):
        self.in_trap = False
        self.kind = AnimalType.lion
        self.team = team
        self.name = team.__str__().split('.')[1] + "_lion"

    # 我想到了一个绝妙的办法，把地形里的河放在初始化里
    # 可不可以把老鼠的位置放进河里，这样就统一了
    def movable(self, start, end):
        if river[end[0]][end[1]] == 0 and ((start[0] == end[0] and abs(start[1] - end[1]) == 1) or (
                start[1] == end[1] and abs(start[0] - end[0]) == 1)):
            return True
        if start[0] == end[0]:
            bigger = max(start[1], end[1])
            smaller = min(start[1], end[1])
            if bigger - smaller == 1:
                return False
            for i in range(smaller+1, bigger):
                if river[start[0]][i] != 1:
                    return False
            return True
        if start[1] == end[1]:
            bigger = max(start[0], end[0])
            smaller = min(start[0], end[0])
            if bigger - smaller == 1:
                return False
            for i in range(smaller+1, bigger):
                if river[i][start[1]] != 1:
                    return False
            return True
        return False


class Elephant(Animal):
    def __init__(self, team):
        self.in_trap = False
        self.kind = AnimalType.elephant
        self.team = team
        self.name = team.__str__().split('.')[1] + "_elephant"

    def eatable(self, otheranimal):
        return False if self.team == otheranimal.team or otheranimal.kind == (AnimalType.mouse or AnimalType.elephant) else True


# 能不能游泳策略模式
class Terrian:
    pass


class River(Terrian):
    def __init__(self):
        self.mark = "~"
        self.name = "river"


class Tower(Terrian):
    def __init__(self, team):
        self.team = team
        self.mark = team.__str__().split('.')[1] + "_$"
        self.name = team.__str__().split('.')[1] + "_crown"


class Trap(Terrian):
    def __init__(self, team):
        self.team = team
        self.mark = team.__str__().split('.')[1] + "_#"
        self.name = team.__str__().split('.')[1] + "_trap"


if __name__ == "__main__":
    make_river()

