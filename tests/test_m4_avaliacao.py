import tempfile
import unittest
from pathlib import Path

from aplicacao.avaliacao.chaves import (
    chave_achado,
)
from aplicacao.avaliacao.motor import (
    MotorAvaliacaoExperimental,
)
from aplicacao.avaliacao.modelos import (
    ClasseGroundTruth,
    ClasseSistema,
    RegistroGroundTruth,
    RegistroSistema,
)
from aplicacao.avaliacao.relatorios import (
    escrever_relatorios,
    hash_ground_truth,
)


class TestAvaliacaoExperimental(
    unittest.TestCase
):

    def _gt(
        self,
        classe=ClasseGroundTruth.POSITIVO,
    ):
        return RegistroGroundTruth(
            projeto="Projeto A",
            arquivo="src/app.py",
            regra="R1",
            linha=10,
            cwe="CWE-22",
            trecho="open(user_input)",
            classe=classe,
        )

    def _sistema(
        self,
        classe=ClasseSistema.CONFIRMADO,
    ):
        return RegistroSistema(
            projeto="Projeto A",
            arquivo="src/app.py",
            regra="R1",
            linha=10,
            cwe="cwe 22",
            trecho="open(user_input)",
            classe=classe,
            origem="veritassec-agent",
        )

    def test_chave_canonica(
        self,
    ):
        self.assertEqual(
            chave_achado(
                self._gt()
            ),
            chave_achado(
                self._sistema()
            ),
        )

    def test_tp(
        self,
    ):
        motor = MotorAvaliacaoExperimental()

        pareados = motor.parear(
            [self._gt()],
            [self._sistema()],
        )

        metricas = (
            motor.calcular_metricas(
                pareados
            )
        )

        self.assertEqual(
            metricas.tp,
            1,
        )

        self.assertEqual(
            metricas.fp,
            0,
        )

        self.assertEqual(
            metricas.precisao,
            1.0,
        )

        self.assertEqual(
            metricas.revocacao,
            1.0,
        )

        motor.validar_invariantes(
            pareados,
            metricas,
        )

    def test_inconclusivo_nao_vira_fn(
        self,
    ):
        motor = MotorAvaliacaoExperimental()

        resultado = self._sistema(
            ClasseSistema.EVIDENCIA_INSUFICIENTE
        )

        pareados = motor.parear(
            [self._gt()],
            [resultado],
        )

        metricas = (
            motor.calcular_metricas(
                pareados
            )
        )

        self.assertEqual(
            metricas.inconclusivos,
            1,
        )

        self.assertEqual(
            metricas.fn,
            0,
        )

    def test_nao_pareado(
        self,
    ):
        motor = MotorAvaliacaoExperimental()

        sistema = self._sistema()
        sistema.linha = 99

        pareados = motor.parear(
            [self._gt()],
            [sistema],
        )

        metricas = (
            motor.calcular_metricas(
                pareados
            )
        )

        self.assertEqual(
            metricas.total_pareados,
            0,
        )

        self.assertEqual(
            metricas.nao_pareados_ground_truth,
            1,
        )

        self.assertEqual(
            metricas.nao_pareados_sistema,
            1,
        )

        motor.validar_invariantes(
            pareados,
            metricas,
        )

    def test_relatorios(
        self,
    ):
        motor = MotorAvaliacaoExperimental()

        gt = [self._gt()]

        pareados = motor.parear(
            gt,
            [self._sistema()],
        )

        metricas = (
            motor.calcular_metricas(
                pareados
            )
        )

        with tempfile.TemporaryDirectory() as tmp:
            raiz = escrever_relatorios(
                tmp,
                pareados,
                metricas,
                hash_ground_truth(gt),
            )

            self.assertTrue(
                (
                    raiz
                    / "resumo-experimental.json"
                ).is_file()
            )

            self.assertTrue(
                (
                    raiz
                    / "matriz-comparacao.csv"
                ).is_file()
            )

            self.assertTrue(
                (
                    raiz
                    / "divergencias.csv"
                ).is_file()
            )

            self.assertTrue(
                (
                    raiz
                    / "nao-pareados.csv"
                ).is_file()
            )


if __name__ == "__main__":
    unittest.main()
