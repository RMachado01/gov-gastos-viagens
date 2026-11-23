import pandas as pd
import pytest

from etl.transform import _converter_real, transformar_dados


def test_converter_real_formato_brasileiro():
    serie = pd.Series(["R$ 1.234,56", "980,00", " 12,5 ", "abc"])
    convertido = _converter_real(serie)
    assert convertido.iloc[:3].tolist() == [1234.56, 980.0, 12.5]
    assert pd.isna(convertido.iloc[3])


def _cru(linhas):
    return pd.DataFrame(linhas, columns=[
        "Identificador do processo de viagem", "Nome do órgão superior", "Tipo de pagamento", "Valor", "ano_arquivo",
    ])


@pytest.mark.parametrize("diaria, passagem", [("DIÁRIA", "PASSAGEM"), ("Diárias", "Passagens")])
def test_agrega_por_processo_e_separa_diarias_e_passagens(diaria, passagem):
    df = transformar_dados(_cru([
        [1, "ministério da saúde", diaria, "300,00", 2023],
        [1, "ministério da saúde", passagem, "1.200,00", 2023],
        [1, "ministério da saúde", "SEGURO", "50,00", 2023],
        [2, "ministério da educação", diaria, "100,00", 2024],
    ]))
    viagem = df.set_index("id_processo").loc[1]
    assert viagem["valor_total"] == 1550.0
    assert viagem["valor_diarias"] == 300.0
    assert viagem["valor_passagens"] == 1200.0
    assert viagem["orgao"] == "Ministério da Saúde"
    assert len(df) == 2


def test_remove_valores_zerados_e_invalidos():
    df = transformar_dados(_cru([
        [1, "ministério x", "DIÁRIA", "0,00", 2023],
        [2, "ministério x", "DIÁRIA", "", 2023],
        [3, "ministério x", "DIÁRIA", "10,00", 2023],
    ]))
    assert df["id_processo"].tolist() == [3]
