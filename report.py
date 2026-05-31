"""Core calculations for FuzzyMIP."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .constants import CLASS_ORDER, EVIDENCE_FACTORS, FUZZY_SCALE


THREAT_MATRIX = {
    "Muito alto": {
        "Muito baixo": "Media",
        "Baixo": "Media",
        "Moderado": "Alta",
        "Alto": "Alta",
        "Muito alto": "Alta",
    },
    "Alto": {
        "Muito baixo": "Baixa",
        "Baixo": "Media",
        "Moderado": "Media",
        "Alto": "Alta",
        "Muito alto": "Alta",
    },
    "Moderado": {
        "Muito baixo": "Baixa",
        "Baixo": "Baixa",
        "Moderado": "Media",
        "Alto": "Alta",
        "Muito alto": "Alta",
    },
    "Baixo": {
        "Muito baixo": "Baixa",
        "Baixo": "Baixa",
        "Moderado": "Media",
        "Alto": "Media",
        "Muito alto": "Alta",
    },
    "Muito baixo": {
        "Muito baixo": "Baixa",
        "Baixo": "Baixa",
        "Moderado": "Baixa",
        "Alto": "Baixa",
        "Muito alto": "Media",
    },
}


OPPORTUNITY_MATRIX = {probability: impacts.copy() for probability, impacts in THREAT_MATRIX.items()}


@dataclass(frozen=True)
class PortfolioStats:
    total_actions: int
    threats: int
    opportunities: int
    high_priority: int
    mean_ip_index: float
    top_action: str


def scale_value(value: object) -> float:
    if isinstance(value, (int, float)):
        return min(1.0, max(0.0, float(value)))

    text = str(value).strip().replace(",", ".")
    try:
        return min(1.0, max(0.0, float(text)))
    except ValueError:
        return float(FUZZY_SCALE.get(str(value), 0.5))


def fuzzy_label(value: object) -> str:
    numeric = scale_value(value)
    if numeric <= 0.20:
        return "Muito baixo"
    if numeric <= 0.40:
        return "Baixo"
    if numeric <= 0.60:
        return "Moderado"
    if numeric <= 0.80:
        return "Alto"
    return "Muito alto"


def format_fuzzy_value(value: object) -> str:
    numeric = scale_value(value)
    return f"{numeric:.2f} ({fuzzy_label(numeric)})"


def is_threat(nature: str) -> bool:
    return str(nature).lower().startswith("amea")


def ip_classification(nature: str, impact: object, probability: object) -> str:
    matrix = THREAT_MATRIX if is_threat(nature) else OPPORTUNITY_MATRIX
    return matrix.get(fuzzy_label(probability), {}).get(fuzzy_label(impact), "Baixa")


def ip_index(impact: object, probability: object) -> float:
    return scale_value(impact) * scale_value(probability)


def decision_result(nature: str, classification: str) -> str:
    if is_threat(nature):
        if classification == "Alta":
            return "Risco critico"
        if classification == "Media":
            return "Risco relevante"
        return "Risco monitorado"

    if classification == "Alta":
        return "Oportunidade prioritaria"
    if classification == "Media":
        return "Oportunidade potencial"
    return "Oportunidade monitorada"


def recommended_action(nature: str, classification: str) -> str:
    if is_threat(nature):
        if classification == "Alta":
            return "Mitigar imediatamente"
        if classification == "Media":
            return "Monitorar e preparar contingencia"
        return "Acompanhar em ciclo periodico"

    if classification == "Alta":
        return "Explorar rapidamente"
    if classification == "Media":
        return "Monitorar e desenvolver condicoes"
    return "Acompanhar como oportunidade de baixa urgencia"


def decision_reading(nature: str, classification: str) -> str:
    return f"{decision_result(nature, classification)}. {recommended_action(nature, classification)}"


def evidence_factor(source: object) -> float:
    label = str(source).strip()
    return float(EVIDENCE_FACTORS.get(label, EVIDENCE_FACTORS["Estimativa fundamentada"]))


def rank_actions(actions: pd.DataFrame) -> pd.DataFrame:
    if actions.empty:
        return pd.DataFrame()

    rows = []
    for _, row in actions.iterrows():
        action = str(row.get("Acao", "")).strip()
        nature = str(row.get("Natureza", "Ameaca")).strip()
        impact = row.get("Impacto", "Moderado")
        probability = row.get("Probabilidade", "Moderado")
        evidence = str(row.get("Base da informacao", "Estimativa fundamentada")).strip()
        classification = ip_classification(nature, impact, probability)
        index = ip_index(impact, probability)
        factor = evidence_factor(evidence)
        adjusted_index = index * factor
        impact_value = scale_value(impact)
        probability_value = scale_value(probability)
        class_weight = CLASS_ORDER.get(classification, 0)
        result = decision_result(nature, classification)
        recommendation = recommended_action(nature, classification)
        rows.append(
            {
                "Acao": action,
                "Natureza": nature,
                "Impacto": format_fuzzy_value(impact),
                "Probabilidade": format_fuzzy_value(probability),
                "Impacto fuzzy": round(impact_value, 2),
                "Probabilidade fuzzy": round(probability_value, 2),
                "Base da informacao": evidence,
                "Fator evidencia": round(factor, 2),
                "Classe I/P": classification,
                "Resultado": result,
                "Indice I/P": round(index, 4),
                "Indice ajustado": round(adjusted_index, 4),
                "Prioridade ordinal": class_weight,
                "Acao recomendada": recommendation,
                "Leitura consultiva": f"{result}. {recommendation}",
            }
        )

    ranking = pd.DataFrame(rows)
    if ranking.empty:
        return ranking
    ranking = ranking.sort_values(
        ["Indice ajustado", "Prioridade ordinal", "Indice I/P", "Acao"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    ranking.insert(0, "Ranking", range(1, len(ranking) + 1))
    return ranking


def portfolio_stats(ranking: pd.DataFrame) -> PortfolioStats:
    if ranking.empty:
        return PortfolioStats(0, 0, 0, 0, 0.0, "")
    threats = int(ranking["Natureza"].astype(str).str.lower().str.startswith("amea").sum())
    opportunities = int(len(ranking) - threats)
    high_priority = int((ranking["Classe I/P"] == "Alta").sum())
    top_action = str(ranking.iloc[0].get("Acao", ""))
    index_column = "Indice ajustado" if "Indice ajustado" in ranking.columns else "Indice I/P"
    mean_ip = float(ranking[index_column].mean())
    return PortfolioStats(
        total_actions=int(len(ranking)),
        threats=threats,
        opportunities=opportunities,
        high_priority=high_priority,
        mean_ip_index=round(mean_ip, 4),
        top_action=top_action,
    )


def _cv_reading(cv: float) -> str:
    if cv <= 0.15:
        return "Baixa dispersao dos indices ajustados."
    if cv <= 0.30:
        return "Dispersao moderada dos indices ajustados."
    return "Alta dispersao; a carteira possui diferencas relevantes de prioridade."


def _hhi_reading(hhi: float) -> str:
    if hhi <= 0.25:
        return "Prioridade distribuida entre varios itens."
    if hhi <= 0.50:
        return "Concentracao intermediaria de prioridade."
    return "Prioridade concentrada em poucos itens."


def statistical_summary(ranking: pd.DataFrame) -> pd.DataFrame:
    if ranking.empty:
        return pd.DataFrame(columns=["Indicador", "Valor", "Leitura"])

    index_column = "Indice ajustado" if "Indice ajustado" in ranking.columns else "Indice I/P"
    indices = pd.to_numeric(ranking[index_column], errors="coerce").fillna(0.0)
    factors = pd.to_numeric(ranking.get("Fator evidencia", pd.Series(dtype=float)), errors="coerce").fillna(1.0)
    count = int(len(indices))
    mean = float(indices.mean())
    median = float(indices.median())
    std = float(indices.std(ddof=0))
    amplitude = float(indices.max() - indices.min())
    cv = float(std / mean) if mean > 0 else 0.0
    high_share = float((ranking["Classe I/P"] == "Alta").mean()) if "Classe I/P" in ranking else 0.0
    evidence_mean = float(factors.mean()) if len(factors) else 1.0
    evidence_discount = 1.0 - evidence_mean
    total = float(indices.sum())
    hhi = float(((indices / total) ** 2).sum()) if total > 0 else 0.0

    return pd.DataFrame(
        [
            {
                "Indicador": "Acoes avaliadas",
                "Valor": f"{count}",
                "Leitura": "Tamanho da carteira analisada no ciclo de priorizacao.",
            },
            {
                "Indicador": "Indice ajustado medio",
                "Valor": f"{mean:.4f}",
                "Leitura": "Nivel medio de prioridade apos abatimento pela qualidade da evidencia.",
            },
            {
                "Indicador": "Mediana do indice ajustado",
                "Valor": f"{median:.4f}",
                "Leitura": "Ponto central da distribuicao, menos sensivel a valores extremos.",
            },
            {
                "Indicador": "Desvio padrao",
                "Valor": f"{std:.4f}",
                "Leitura": "Dispersao absoluta dos indices ajustados.",
            },
            {
                "Indicador": "Coeficiente de variacao",
                "Valor": f"{cv:.2%}",
                "Leitura": _cv_reading(cv),
            },
            {
                "Indicador": "Amplitude",
                "Valor": f"{amplitude:.4f}",
                "Leitura": "Diferenca entre o maior e o menor indice ajustado.",
            },
            {
                "Indicador": "Prioridade alta",
                "Valor": f"{high_share:.2%}",
                "Leitura": "Proporcao de itens classificados como risco critico ou oportunidade prioritaria.",
            },
            {
                "Indicador": "Fator medio de evidencia",
                "Valor": f"{evidence_mean:.2f}",
                "Leitura": "Proximidade media dos dados em relacao a uma base real/mensurada.",
            },
            {
                "Indicador": "Abatimento medio por evidencia",
                "Valor": f"{evidence_discount:.2%}",
                "Leitura": "Reducao media aplicada quando as informacoes sao estimadas ou pouco sustentadas.",
            },
            {
                "Indicador": "Concentracao HHI",
                "Valor": f"{hhi:.4f}",
                "Leitura": _hhi_reading(hhi),
            },
        ]
    )


def consultive_conclusion(ranking: pd.DataFrame) -> str:
    stats = portfolio_stats(ranking)
    if stats.total_actions == 0:
        return "Nao ha acoes cadastradas para conclusao consultiva."

    high_share = stats.high_priority / stats.total_actions
    top = ranking.iloc[0]
    nature = str(top.get("Natureza", ""))
    action = str(top.get("Acao", ""))
    classification = str(top.get("Classe I/P", ""))

    if stats.threats > stats.opportunities:
        portfolio_reading = "A carteira avaliada apresenta predominio de ameacas."
    elif stats.opportunities > stats.threats:
        portfolio_reading = "A carteira avaliada apresenta predominio de oportunidades."
    else:
        portfolio_reading = "A carteira avaliada apresenta equilibrio entre ameacas e oportunidades."

    if high_share >= 0.5:
        urgency = "Ha concentracao relevante de itens classificados como prioridade alta."
    elif stats.high_priority > 0:
        urgency = "Ha itens de prioridade alta, mas sem predominio na carteira."
    else:
        urgency = "Nao ha itens classificados como prioridade alta no conjunto analisado."

    if is_threat(nature):
        top_reading = f"A primeira acao do ranking e '{action}', tratada como ameaca de classe {classification}, sugerindo resposta de mitigacao."
    else:
        top_reading = f"A primeira acao do ranking e '{action}', tratada como oportunidade de classe {classification}, sugerindo avaliacao para captura de valor."

    return f"{portfolio_reading} {urgency} {top_reading}"
