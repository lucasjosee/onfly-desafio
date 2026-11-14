"""Testes adicionais: leitura completa do arquivo de reservas."""

from helpers import run_cli


def test_cli_reads_entire_file(tmp_path):
    """Todas as 250 linhas do CSV são lidas, sem corte em um limite fixo."""
    rows = [{"reservation_id": f"R-{index}"} for index in range(1, 251)]
    report = run_cli(tmp_path, rows)
    assert report["summary"]["total_reservations"] == 250
