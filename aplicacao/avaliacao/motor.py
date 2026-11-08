from __future__ import annotations

from collections import Counter

from .chaves import chave_achado
from .modelos import (
    ClasseGroundTruth,
    ClasseSistema,
    MetricasExperimentais,
    Pareamento,
    RegistroGroundTruth,
    RegistroSistema,
)


class ErroGroundTruthDuplicado(ValueError):
    pass


class ErroResultadoDuplicado(ValueError):
    pass


class MotorAvaliacaoExperimental:

    @staticmethod
    def parear(
        ground_truth: list[RegistroGroundTruth],
        resultados: list[RegistroSistema],
    ) -> list[Pareamento]:

        gt_por_chave: dict[
            str,
            RegistroGroundTruth,
        ] = {}

        sistema_por_chave: dict[
            str,
            RegistroSistema,
        ] = {}

        for registro in ground_truth:
            chave = chave_achado(registro)

            if chave in gt_por_chave:
                raise ErroGroundTruthDuplicado(
                    "ground truth possui chave "
                    f"duplicada: {chave}"
                )

            gt_por_chave[chave] = registro

        for registro in resultados:
            chave = chave_achado(registro)

            if chave in sistema_por_chave:
                raise ErroResultadoDuplicado(
                    "resultado possui chave "
                    f"duplicada: {chave}"
                )

            sistema_por_chave[chave] = registro

        chaves = sorted(
            set(gt_por_chave)
            | set(sistema_por_chave)
        )

        return [
            Pareamento(
                chave=chave,
                ground_truth=(
                    gt_por_chave.get(chave)
                ),
                sistema=(
                    sistema_por_chave.get(chave)
                ),
            )
            for chave in chaves
        ]

    @staticmethod
    def calcular_metricas(
        pareamentos: list[Pareamento],
    ) -> MetricasExperimentais:

        tp = fp = tn = fn = 0

        inconclusivos = 0
        erros = 0
        nao_avaliados = 0

        total_gt = sum(
            1
            for p in pareamentos
            if p.ground_truth is not None
        )

        total_sistema = sum(
            1
            for p in pareamentos
            if p.sistema is not None
        )

        pareados = [
            p
            for p in pareamentos
            if p.pareado
        ]

        for p in pareados:
            assert p.ground_truth is not None
            assert p.sistema is not None

            gt = p.ground_truth.classe
            sis = p.sistema.classe

            if (
                sis
                == ClasseSistema.EVIDENCIA_INSUFICIENTE
            ):
                inconclusivos += 1
                continue

            if sis == ClasseSistema.ERRO:
                erros += 1
                continue

            if sis == ClasseSistema.NAO_AVALIADO:
                nao_avaliados += 1
                continue

            if (
                gt == ClasseGroundTruth.POSITIVO
                and sis == ClasseSistema.CONFIRMADO
            ):
                tp += 1

            elif (
                gt == ClasseGroundTruth.NEGATIVO
                and sis == ClasseSistema.CONFIRMADO
            ):
                fp += 1

            elif (
                gt == ClasseGroundTruth.NEGATIVO
                and sis == ClasseSistema.REFUTADO
            ):
                tn += 1

            elif (
                gt == ClasseGroundTruth.POSITIVO
                and sis == ClasseSistema.REFUTADO
            ):
                fn += 1

        def divisao(
            numerador: int,
            denominador: int,
        ) -> float | None:

            if denominador == 0:
                return None

            return numerador / denominador

        precisao = divisao(
            tp,
            tp + fp,
        )

        revocacao = divisao(
            tp,
            tp + fn,
        )

        especificidade = divisao(
            tn,
            tn + fp,
        )

        if (
            precisao is None
            or revocacao is None
            or precisao + revocacao == 0
        ):
            f1 = None
        else:
            f1 = (
                2
                * precisao
                * revocacao
                / (
                    precisao
                    + revocacao
                )
            )

        return MetricasExperimentais(
            total_ground_truth=total_gt,
            total_resultados_sistema=(
                total_sistema
            ),
            total_pareados=len(pareados),
            nao_pareados_ground_truth=sum(
                1
                for p in pareamentos
                if (
                    p.ground_truth is not None
                    and p.sistema is None
                )
            ),
            nao_pareados_sistema=sum(
                1
                for p in pareamentos
                if (
                    p.ground_truth is None
                    and p.sistema is not None
                )
            ),
            tp=tp,
            fp=fp,
            tn=tn,
            fn=fn,
            inconclusivos=inconclusivos,
            erros=erros,
            nao_avaliados=nao_avaliados,
            precisao=precisao,
            revocacao=revocacao,
            especificidade=especificidade,
            f1=f1,
        )

    @staticmethod
    def validar_invariantes(
        pareamentos: list[Pareamento],
        metricas: MetricasExperimentais,
    ) -> None:

        gt = sum(
            1
            for p in pareamentos
            if p.ground_truth is not None
        )

        sistema = sum(
            1
            for p in pareamentos
            if p.sistema is not None
        )

        if gt != metricas.total_ground_truth:
            raise AssertionError(
                "invariante TOTAL_GROUND_TRUTH violada"
            )

        if (
            sistema
            != metricas.total_resultados_sistema
        ):
            raise AssertionError(
                "invariante TOTAL_RESULTADOS_SISTEMA "
                "violada"
            )

        if (
            metricas.total_pareados
            + metricas.nao_pareados_ground_truth
            != metricas.total_ground_truth
        ):
            raise AssertionError(
                "invariante de pareamento GT violada"
            )

        if (
            metricas.total_pareados
            + metricas.nao_pareados_sistema
            != metricas.total_resultados_sistema
        ):
            raise AssertionError(
                "invariante de pareamento "
                "do sistema violada"
            )
