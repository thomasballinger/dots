"""Dots!"""
#encoding: utf8
import random
import itertools
import functools
import sys

from curtsies.fmtfuncs import *
from curtsies.terminal import  Terminal
from curtsies.fsarray import fsarray, FSArray

class Board(object):
    def __init__(self, width, height, ncolors):
        self._rows = [[random.choice(range(ncolors)) for _ in range(width)] for _ in range(height)]
        self.width = width
        self.height = height
    rows = property(lambda self: tuple(tuple(row) for row in self._rows))
    columns = property(lambda self: zip(*self._rows))
    spots = property(lambda self: tuple(spot for row in self._rows for spot in row))

    def __getitem__(self, (x, y)):
        assert 0 <= x < self.width and 0 <= y < self.height
        return self._rows[y][x]

    def neighbors(self, x, y):
        spots = [(x + d[0], y + d[1])
                for d in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if (0 <= x + d[0] < self.width) and (0 <= y + d[1] < self.height)]
        return spots

    def matching_neighbors(self, x, y):
        return [neighbor for neighbor in self.neighbors(x, y) if self[neighbor] == self[x, y]]

    def extensions(self, x, y, visited=tuple()):
        further_paths = tuple(sum([self.extensions(*neighbor, visited=(visited + ((x,y),)))
                                   for neighbor in self.matching_neighbors(x, y)
                                   if neighbor not in visited], tuple()))
        return tuple(((x, y),) + path for path in (further_paths + (tuple(),)))

    def moves_for_dot(self, x, y):
        return tuple(path for path in self.extensions(x, y) if len(path) > 1)

    def moves(self):
        return sum([self.moves_for_dot(x, y) for x in range(self.width) for y in range(self.height)], tuple())

    def unique_moves(self):
        dot_sets = set()
        moves = []
        for move in self.moves():
            dot_set = frozenset(move)
            if dot_set not in dot_sets:
                dot_sets.add(frozenset(move))
                moves.append(move)
        return moves

    def unique_moves_ascending(self):
        moves = self.unique_moves()
        moves.sort(key=len)
        return moves

    def best_move(self):
        return max(self.moves(), key=len)

    def get_array(self, path=[]):
        h_space = 2
        v_space = 1
        line = lambda p1, p2: p1 in path and p2 in path and abs(path.index(p1) - path.index(p2)) == 1
        def color(num): return lambda s: bold([magenta, blue, red, green, yellow][num](s))
        lines = [''] * v_space
        for y, row in enumerate(self.rows):
            lines.append(' '*h_space)
            space = ' '*h_space
            for x, dot in enumerate(row):
                lines[-1] += color(dot)(u'\u25cf')
                if line((x, y), (x+1, y)):
                    lines[-1] += color(dot)('--')
                else:
                    lines[-1] += ('  ')
                if line((x, y), (x, y+1)):
                    space += color(dot)('|'+' '*h_space)
                else:
                    space += ' '*(1+h_space)
            [lines.append(space) for _ in range(v_space)]
        return fsarray(lines)

    def display(self):
        a = self.get_array()
        a.dumb_display()

def fit(fs_array, fs_arrays, border=True):
    if border:
        fs_arrays = [fsarray(['+'+'-'*fsa.width+'+'] +
                             ['|'+line+'|' for line in fsa.rows] +
                             ['+'+'-'*fsa.width+'+'])
                     for fsa in fs_arrays]
    for fsa in fs_arrays:
        if fsa.width > fs_array.width:
            raise ValueError("input array won't fit inside composite array")

    top_free = [0] * fs_array.width

    def fits(fsa, row, col):
        if fsa.width > len(top_free) - col: return False
        return all(top_free[col] <= r for r in range(row, row+fsa.width))

    cur_fsa = fs_arrays.pop(0)
    for row, col in ((row, col) for row in xrange(1000000) for col in range(fs_array.width)):
        if fits(cur_fsa, row, col):
            fs_array[row:row+cur_fsa.height, col:col+cur_fsa.width] = cur_fsa
            for col in range(col, col+cur_fsa.width):
                top_free[col] += cur_fsa.height
            if not fs_arrays:
                return
            cur_fsa = fs_arrays.pop(0)

def show_moves():
    with Terminal() as t:
        _, term_width = t.get_screen_size()
    b = Board(6, 6, 5)
    moves = b.unique_moves_ascending()
    boards = [b.get_array(move) for move in moves]
    #for board in boards:
    #    board.dumb_display()
    a = FSArray(0, term_width)
    fit(a, boards, border=False)
    a.dumb_display()

sys.setrecursionlimit(30)

def simple_tests():
    b = Board(6, 6, 5)
    print b._rows
    print b.rows
    print b.columns
    print b.spots
    b.display()
    print 'neighbors:', b.neighbors(1, 1)
    print 'matching neighbors:', b.matching_neighbors(1, 1)
    print '--'
    print b.moves_for_dot(1,1)
    print b.moves()
    print b.best_move()
#b.display(b.best_move())

if __name__ == '__main__':
    while True:
        show_moves()
        raw_input('-'*20)
