#!/usr/bin/env python3
from Sudoku import *
import itertools

def get_advancement_options(sudoku):
    """Generates a list of advancement options for a sudoku puzzle, each one consisting of a set alternatives where each alternative is a (x, y, value) tuple defining the move"""
    square_possibilities_cache = {}
    section_possibilities_cache = {}
    for square in sudoku:
        if not square:
            possibilities = square_values.difference(itertools.chain.from_iterable((cur.value for cur in section) for section in square.sections))
            square_possibilities_cache[square]=possibilities
            yield frozenset((square.x,square.y,value) for value in possibilities)
    for section in sudoku.sections:
        missing = square_values.difference(square.value for square in section)
        for value in missing:
            possibilities = frozenset(square for square in section if not square and value in square_possibilities_cache[square])
            section_possibilities_cache[(section,value)] = possibilities
            yield frozenset((square.x,square.y,value) for square in possibilities)

def select_advancement_option(sudoku):
    """Selects the first unambigious move found, or if no unambigious move is found selects one that is the least ambigious"""
    shortest_len = None
    shortest = None
    for options in get_advancement_options(sudoku):
        l = len(options)
        if l == 0:
            return (l,options)
        if l == 1:
            return (l,options)
        if (shortest is None) or (l < shortest_len):
            shortest_len = l
            shortest = options
    return (shortest_len,shortest)

def find_solutions(start, verbose):
    """Generates a list of all solutions to a sudoku puzzle"""
    start = MutableSudokuData(start)
    sudoku = SudokuView(start)
    active = [start]
    while active:
        current = active.pop(0)
        sudoku.data = current
        if verbose:
            print("{}\n".format(sudoku))
        if sudoku.solved:
            yield TupleSudokuData(current)
            continue
        option_split,options = select_advancement_option(sudoku)
        if option_split==0:
            continue
        elif option_split==1:
            x,y,value = next(iter(options))
            current[x,y]=value
            active.append(current)
        else:
            split = [current]+[MutableSudokuData(current) for _ in range(option_split-1)]
            for data,(x,y,value) in zip(split,options):
                data[x,y]=value
            active.extend(split)

def solve(start: SudokuData, verbose = False):
    """Simple wrapper around find_solutions that prints the data for insepection"""
    printer = SudokuView(start)
    print("Start:\n{}\n".format(printer))
    for solution in find_solutions(start,verbose):
        printer.data = solution
        print("Solution:\n{}\n".format(printer))

if __name__ == "__main__":
    test = data_from_string("""
-21----34
9---2-1-8
75-814-9-
6--17---3
-472-9--5
-35-6-917
4183-2-79
--698-34-
-9---7--1
""")
    solve(test)
