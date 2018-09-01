#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Sequence, Union, overload, List, Iterator, Optional, NewType, AbstractSet

square_values = frozenset(range(1,10))

Index = NewType('Index',int)
ActiveSudokuValue = NewType('ActiveSudokuValue',int)
SudokuValue = NewType('SudokuValue',Optional[ActiveSudokuValue])

@dataclass(frozen=True)
class SudokuSquare:
    """A view of a single square of a sudoku"""
    __slots__=('source','x','y')
    source: "SudokuView"
    x: Index
    y: Index
    def __init__(self, source: "SudokuView", x: Index, y: Index):
        if not isinstance(source, SudokuView):
            raise TypeError()
        if (0 > x > 9):
            raise ValueError()
        if (0 > y > 9):
            raise ValueError()
        object.__setattr__(self,'source',source)
        object.__setattr__(self,'x',x)
        object.__setattr__(self,'y',y)
    @property
    def value(self) -> SudokuValue:
        return self.source.data[self.x, self.y]
    @value.setter
    def value(self, value: SudokuValue):
        self.source.data[x, y] = value
    @property
    def row(self) -> "SudokuRow":
        return self.source.rows[self.y]
    @property
    def column(self) -> "SudokuColumn":
        return self.source.columns[self.x]
    @property
    def box(self) -> "SudokuBox":
        return self.source.boxes[(self.x//3)+3 * (self.y//3)]
    @property
    def sections(self) -> Tuple["Sudoku9","Sudoku9","Sudoku9"]: return (self.row,self.column,self.box)
    def __repr__(self) -> str:
        if self.value is None:
            return "<SodukuSquare at {},{}>".format(self.x,self.y)
        else:
            return "<SodukuSquare[{}] at {},{}>".format(self.value,self.x,self.y)
    def __bool__(self) -> bool:
        return self.value is not None
    def __str__(self) -> str:
        return "-" if self.value is None else str(self.value)

@dataclass(frozen=True)
class Sudoku9(Sequence[SudokuSquare]):
    """A view of a duplicate free section (row/column/box) of a sudoku"""
    __slots__=('source','position')
    source: "SudokuView"
    position: Index
    def __init__(self, source: "SudokuView", position: Index):
        if not isinstance(source, SudokuView):
            raise TypeError()
        if (0 > position > 9):
            raise ValueError()
        object.__setattr__(self,'source',source)
        object.__setattr__(self,'position',position)
    @overload
    def __getitem__(self, index: int) -> SudokuSquare:
        ...
    @overload
    def __getitem__(self, index: slice) -> List[SudokuSquare]:
        ...
    def __getitem__(self, index):
        if isinstance(index,slice):
            return [self.source[self._get_subindex_position(i)] for i in range(*index.indices(9))]
        if isinstance(index,int):
            if 0 > index > 9:
                raise IndexError
            return self.source[self._get_index_position(index)]
        else:
            try:
                index = index.__index__()
            except AttributeError:
                pass
            else:
                if isinstance(index,int):
                    if 0 > index > 9:
                        raise IndexError
                    return self.source[self._get_index_position(subindex)]
                else:
                    raise TypeError("__index__ returned non-int (type {})".format(type(index).__name__))
        raise TypeError("{} indexes must be integers or slices, not {}".format(type(self).__name__,type(index).__name__))
    def __len__(self) -> int:
        return 9
    def __iter__(self) -> Iterator[SudokuSquare]:
        for i in range(9):
            yield self.source[self._get_index_position(i)]
    def __reversed__(self) -> Iterator[SudokuSquare]:
        for i in reversed(range(9)):
            yield self.source[self._get_index_position(i)]
    def __contains__(self, value: Union[SudokuValue,SudokuSquare]) -> bool:
        if (value is None or (isinstance(value,int))):
            return any(square.value == value for square in self)
        if isinstance(value, SudokuSquare):
            return self._contains_position(value.x,value.y)
        raise TypeError
    def index(self, value: Union[SudokuValue,SudokuSquare], start: int = 0, stop: Optional[int] = None):
        if (value is None or isinstance(value,int)):
            for i,square in enumerate(self):
                if square.value == value:
                    return i
            raise IndexError
        if isinstance(square, SudokuSquare):
            if value.source is not self.source:
                raise ValueError
            i = self._get_position_index(value.x,value.y)
            if start > i:
                raise IndexError
            if stop is not None:
                if i >= stop:
                    raise IndexError
            return i
    def count(self, value: SudokuSquare) -> int:
        return 1 if value in self else 0
    @abstractmethod
    def _get_index_position(self, index: Index) -> Tuple[Index,Index]:
        raise NotImplementedError
    @abstractmethod
    def _contains_position(self, x: Index, y: Index) -> bool:
        raise NotImplementedError
    @abstractmethod
    def _get_position_index(self, x: Index, y: Index) -> Index:
        raise NotImplementedError

class SudokuRow(Sudoku9):
    """A view of a sudoku row"""
    __slots__=()
    def _get_index_position(self, index: Index) -> Tuple[Index,Index]:
        return (index,self.position)
    def _contains_position(self, x: Index, y: Index) -> bool:
        return self.position == y
    def _get_position_index(self, x: Index, y: Index) -> Index:
        if self.position != y:
            raise IndexError
        return x
    def __str__(self):
        return "".join(map(str,self))

class SudokuColumn(Sudoku9):
    """A view of a sudoku column"""
    __slots__=()
    def _get_index_position(self, index: Index) -> Tuple[Index,Index]:
        return (self.position,index)
    def _contains_position(self, x: Index, y: Index) -> bool:
        return self.position == x
    def _get_position_index(self, x: Index, y: Index) -> Index:
        if self.position != x:
            raise IndexError
        return y
    def __str__(self):
        return "\n".join(map(str,self))

class SudokuBox(Sudoku9):
    """A view of a sudoku 3x3 box"""
    __slots__=()
    def _get_index_position(self, index: Index) -> Tuple[Index,Index]:
        return (self.position%3 * 3 + index % 3,self.position//3 * 3 + index//3)
    def _contains_position(self, x: Index, y: Index) -> bool:
        return self.position == (x//3)+3 * (y//3)
    def _get_position_index(self, x: Index, y: Index) -> Index:
        x = x - (self.position % 3 * 3)
        y = y - (self.position // 3 * 3)
        return x + y * 3
    def __str__(self):
        return "".join(map(str,(
            self[0],self[1],self[2],"\n",
            self[3],self[4],self[5],"\n",
            self[6],self[7],self[8])))

class SudokuView:
    """A view of an entire sudoku"""
    __slots__=('squares','rows','columns','boxes','data')
    squares: Tuple[SudokuSquare,...]
    rows: Tuple[SudokuRow,...]
    columns: Tuple[SudokuColumn,...]
    boxes: Tuple[SudokuBox,...]
    data: "SudokuData"
    def __init__(self, data: "SudokuData"):
        if not isinstance(data, SudokuData):
            raise TypeError
        object.__setattr__(self,'squares',tuple(SudokuSquare(self,x,y) for y in range(9) for x in range(9)))
        object.__setattr__(self,'rows',tuple(SudokuRow(self,position) for position in range(9)))
        object.__setattr__(self,'columns',tuple(SudokuColumn(self,position) for position in range(9)))
        object.__setattr__(self,'boxes',tuple(SudokuBox(self,position) for position in range(9)))
        object.__setattr__(self,'data',data)
    @property
    def sections(self) -> Tuple[Sudoku9,...]: return self.rows+self.columns+self.boxes
    def __getitem__(self, target: Tuple[Index,Index]) -> SudokuSquare:
        x, y = target
        if(0 > x > 9):
            raise IndexError()
        if(0 > y > 9):
            raise IndexError()
        return self.squares[x + 9 * y]
    def __setitem__(self, target: Tuple[Index,Index], value: SudokuValue):
        x, y = target
        if(0 > x > 9):
            raise IndexError()
        if(0 > y > 9):
            raise IndexError()
        self.data[x, y] = value
    def __str__(self) -> str:
        return "\n".join(map(str,self.rows))
    def __iter__(self):
        yield from self.squares
    def __len__(self):
        return 81
    @property
    def solved(self) -> bool:
        return all(square.value is not None for square in self) and self.validate()
    def validate(self) -> bool:
        for section in self.sections:
            values = set(square_values)
            for square in section:
                value = square.value
                if value is not None:
                    try:
                        values.remove(square.value)
                    except KeyError:
                        return False
        return True
    def __setattr__(self,key,value):
        if(key=='data'):
            if(isinstance(value,SudokuData)):
                object.__setattr__(self,'data',value)
            else:
                raise TypeError
        elif key in self.__slots__:
            raise TypeError
        else:
            raise AttributeError
                    
class SudokuData(metaclass = ABCMeta):
    """Abstract class used to store the actual data of a sudoku puzzle without the logic of the game structure itself"""
    __slots__=tuple()
    @abstractmethod
    def __getitem__(self, position: Tuple[Index,Index]) -> SudokuValue:
        raise NotImplementedError
    def __setitem__(self, position: Tuple[Index,Index], value: SudokuValue):
        raise TypeError("{} does not support item assignment".format(type(self).__name__))
    def __iter__(self) -> Iterator[SudokuValue]:
        for y in range(9):
            for x in range(9):
                yield self[x,y]
    def __len__(self) -> int:
        return 81

class BlankSudokuData(SudokuData):
    """Trivial sudoku data that contains nothing filled in"""
    __slots__=tuple()
    def __getitem__(self, position: Tuple[Index,Index]) -> SudokuValue:
        return None

class SudokuDataProxy(SudokuData):
    """Simple proxy that redirects the lookups"""
    __slots__=('data')
    def __init__(self,data: SudokuData):
        self.data = data
    def __getitem__(self, position: Tuple[Index,Index]) -> SudokuValue:
        return self.data[position]
    def __setitem__(self, position: Tuple[Index,Index], value: SudokuValue):
        self.data[position] = value
    
class TupleSudokuData(tuple,SudokuData):
    """Immutable sudoku data consisting of a 81 length tuple"""
    def __init__(self, data):
        if(tuple.__len__(self) != 81):
            raise ValueError
        for value in self:
            if value is None:
                continue
            if not isinstance(value,int):
                raise TypeError
            if 1 > value > 10:
                raise ValueError
    def __getitem__(self, position: Tuple[Index,Index]) -> SudokuValue:
        return tuple.__getitem__(self,position[0]+position[1]*9)

class MutableSudokuData(SudokuData):
    """Mutable sudoku data"""
    __slots__=('_data')
    def __init__(self, data):
        self._data = list(data)
    def __getitem__(self, position: Tuple[Index,Index]) -> SudokuValue:
        return self._data[position[0]+position[1]*9]
    def __setitem__(self, position: Tuple[Index,Index], value: SudokuValue):
        self._data[position[0]+position[1]*9] = value

def data_from_string(source: str) -> TupleSudokuData:
    """The inverse of how sudoku views are printed"""
    accepted_characters=set(map(str,range(10)))
    accepted_characters.add('-')
    lines = source.strip().split("\n")
    if(len(lines)!=9):
        raise ValueError()
    if(not all(len(line)==9 for line in lines)):
        raise ValueError()
    data = "".join(lines)
    if(not (set(data).issubset(accepted_characters))):
        raise ValueError()
    return TupleSudokuData(None if val=='-' else int(val) for val in data)

