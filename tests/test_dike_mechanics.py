import logging

import lada.fellow.board
import lada.models

from lada.constants import *

from tests.fixtures import *

log = logging.getLogger(__name__)


def test_clear_board_clears_positions(users):
    for i, position in enumerate(POSITIONS_ALL):
        users[i].set_board(position, True)

    lada.fellow.board.clear_board()

    for fellow in lada.models.Fellow.query.all():
        for position_flag in POSITIONS_ALL:
            log.debug(f"Checking {fellow} for {position_flag}")
            assert not fellow.check_board(position_flag)


def test_clear_board_keeps_fellow_board_flag(users):
    users[0].set_board(FELLOW_BOARD, True)

    lada.fellow.board.clear_board()

    assert users[0].check_board(FELLOW_BOARD)
