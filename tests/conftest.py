from __future__ import annotations

import pytest

from pyzet import constants as const
from pyzet.main import main

TEST_CFG = ('--config', f'testing/{const.CONFIG_FILE}')


@pytest.fixture()
def pyzet_init(tmp_path):
    init_dir = tmp_path.as_posix()
    main([*TEST_CFG, 'init', init_dir])
    return init_dir
