from tictactoe.ui.scenes.game import format_time, key_to_cell


def test_teclas_seguem_layout_do_teclado_numerico():
    assert key_to_cell(7) == (0, 0)
    assert key_to_cell(9) == (0, 2)
    assert key_to_cell(5) == (1, 1)
    assert key_to_cell(1) == (2, 0)
    assert key_to_cell(3) == (2, 2)


def test_formatacao_do_cronometro():
    assert format_time(0) == "00:00"
    assert format_time(75.9) == "01:15"
