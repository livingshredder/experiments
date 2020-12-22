from enum import Enum


class PegType(Enum):
    EMPTY = 0
    PEG = 1
    NOR = 2


ROW_LENGTH = 24


PEG_BOARDS = [
    # board 1
    [
        # rows 1-4
        [
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.NOR,
            PegType.PEG
        ],
        [
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.PEG,
            PegType.EMPTY,
            PegType.PEG,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG
        ],
        [PegType.EMPTY] * ROW_LENGTH,
        [PegType.EMPTY] * ROW_LENGTH
    ],

    # board 2
    [
        [PegType.EMPTY] * ROW_LENGTH,
        [PegType.EMPTY] * ROW_LENGTH,
        [PegType.EMPTY] * ROW_LENGTH,
        [PegType.EMPTY] * ROW_LENGTH
    ],

    # board 3
    [
        [
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG
        ],
        [
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.NOR,
            PegType.EMPTY,
            PegType.NOR,
            PegType.PEG,
            PegType.EMPTY,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR
        ],
        [PegType.EMPTY] * ROW_LENGTH,
        [PegType.EMPTY] * ROW_LENGTH
    ],

    # board 4
    [
        [
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
        ],
        [
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.PEG,
            PegType.NOR,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
            PegType.EMPTY,
        ],
        [PegType.EMPTY] * ROW_LENGTH,
        [PegType.EMPTY] * ROW_LENGTH
    ]
]

PEG_MAP = {
    PegType.EMPTY: ' ',
    PegType.PEG: 'P',
    PegType.NOR: 'N'
}

def print_pegboard():
    for i, board in enumerate(PEG_BOARDS):
        print(f'Board {i+1}')
        boardstr = '/' + ('='*(ROW_LENGTH+2)) + '\\\n'
        for row in board:
            rowstr = ''
            for peg in row:
                rowstr += PEG_MAP[peg]
            boardstr += f'| {rowstr} |\n'

        boardstr += '\\' + ('='*(ROW_LENGTH+2)) + '/'
        print(boardstr + '\n')

print_pegboard()
