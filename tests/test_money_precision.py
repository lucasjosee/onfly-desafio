"""Testes adicionais: precisão monetária na conversão de câmbio."""

from helpers import run_cli


def test_currency_conversion_does_not_use_float(tmp_path):
    """0.75 USD * 5.42 = 4.065 exato, que arredonda para 4.07; via float daria 4.0649999... e viraria 4.06."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "currency": "USD", "amount": "0.75"},
        ],
    )
    assert report["summary"]["total_amount_brl"] == "4.07"
