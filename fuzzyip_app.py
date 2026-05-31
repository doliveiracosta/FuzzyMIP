"""Streamlit app for fuzzy impact/probability prioritization."""

from __future__ import annotations

import base64
import mimetypes
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from fuzzyip.constants import (
    APP_NAME,
    APP_OWNER_LABEL,
    APP_SUBTITLE,
    CLASS_COLORS,
    EVIDENCE_FACTORS,
    FUZZY_SCALE,
    GITHUB_URL,
    LINKEDIN_URL,
    NATURES,
    ORCID_URL,
    PDF_FILE_NAME,
)
from fuzzyip.core import (
    OPPORTUNITY_MATRIX,
    THREAT_MATRIX,
    consultive_conclusion,
    fuzzy_label,
    ip_index,
    portfolio_stats,
    rank_actions,
    scale_value,
)
from fuzzyip.report import pdf_bytes


def asset_path(*names: str) -> Path | None:
    base = Path(__file__).resolve().parent
    search_dirs = [base / "assets", Path.cwd() / "assets", Path("assets"), base, Path.cwd()]
    for directory in search_dirs:
        for name in names:
            candidate = directory / name
            if candidate.exists():
                return candidate
    return None


def asset_data_uri(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def init_state() -> None:
    defaults = {
        "project": {
            "Projeto": "Priorizacao fuzzy de acoes estrategicas",
            "Organizacao": "",
            "Responsavel": "",
            "Horizonte": "12 meses",
            "Contexto decisorio": "",
        },
        "actions": pd.DataFrame(
            [
                {
                    "Acao": "Mitigar dependencia de fornecedor critico",
                    "Natureza": "Ameaca",
                    "Impacto": "Muito alto",
                    "Probabilidade": "Alto",
                    "Base da informacao": "Estimativa fundamentada",
                },
                {
                    "Acao": "Explorar novo canal digital",
                    "Natureza": "Oportunidade",
                    "Impacto": "Alto",
                    "Probabilidade": "Moderado",
                    "Base da informacao": "Dado real / mensurado",
                },
                {
                    "Acao": "Reduzir retrabalho operacional",
                    "Natureza": "Ameaca",
                    "Impacto": "Moderado",
                    "Probabilidade": "Muito alto",
                    "Base da informacao": "Percepcao preliminar",
                },
                {
                    "Acao": "Criar parceria estrategica",
                    "Natureza": "Oportunidade",
                    "Impacto": "Moderado",
                    "Probabilidade": "Baixo",
                    "Base da informacao": "Baixa evidencia",
                },
            ]
        ),
        "ranking": pd.DataFrame(),
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_cover() -> None:
    st.markdown(
        """
        <style>
        .institutional-logos {
            display: flex;
            align-items: center;
            gap: 22px;
            margin: 0.2rem 0 1rem;
        }
        .institutional-logos img {
            object-fit: contain;
            width: auto;
            display: block;
        }
        .institutional-logos .logo-upe { height: 52px; }
        .institutional-logos .logo-poli { height: 54px; }
        .institutional-logos .logo-ppgec { height: 48px; }
        .institutional-logo-fallback {
            min-width: 86px;
            height: 42px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            color: #1f2937;
            font-size: .78rem;
            font-weight: 700;
        }
        .author-links {
            display: flex;
            align-items: center;
            gap: 18px;
            margin: .55rem 0 1.2rem;
        }
        .author-links a {
            color: #6b7280;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 7px;
            font-size: .92rem;
        }
        .author-links img {
            width: 18px;
            height: 18px;
            object-fit: contain;
        }
        .metric-band {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 14px;
            margin: 1rem 0 1.2rem;
        }
        .metric-card {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 12px 14px;
            background: #fff;
        }
        .metric-card span {
            display: block;
            color: #6b7280;
            font-size: .82rem;
            margin-bottom: 4px;
        }
        .metric-card strong {
            font-size: 1.65rem;
            color: #111827;
        }
        .matrix-table {
            border-collapse: collapse;
            width: 100%;
            table-layout: fixed;
            margin-top: .5rem;
            font-size: .82rem;
        }
        .matrix-table th,
        .matrix-table td {
            border: 1px solid #9ca3af;
            padding: 8px 6px;
            text-align: center;
            vertical-align: middle;
        }
        .matrix-table th {
            background: #dbeafe;
            color: #111827;
            font-weight: 700;
        }
        .class-chip {
            display: inline-flex;
            min-width: 86px;
            justify-content: center;
            padding: 7px 10px;
            border-radius: 7px;
            font-weight: 700;
            box-shadow: inset 0 0 0 1px rgba(0,0,0,.10);
        }
        .ip-box {
            border: 1px solid #bfdbfe;
            background: #eff6ff;
            color: #1e3a8a;
            border-radius: 7px;
            padding: 8px 10px;
            text-align: center;
            font-weight: 700;
        }
        .app-subtitle-small {
            color: #6b7280;
            font-size: 1.02rem;
            line-height: 1.45;
            margin: -0.35rem 0 1rem;
        }
        .reference-table {
            width: 100%;
            border-collapse: collapse;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            overflow: hidden;
            font-size: .92rem;
        }
        .reference-table th,
        .reference-table td {
            border-bottom: 1px solid #e5e7eb;
            padding: 10px 11px;
            text-align: center;
            vertical-align: top;
        }
        .reference-table th {
            background: #f8fafc;
            color: #475569;
            font-weight: 600;
            text-align: center;
        }
        .reference-table tr:last-child td {
            border-bottom: none;
        }
        .priority-critical td {
            background: #dc2626;
            color: #ffffff;
        }
        .priority-attention td {
            background: #fb923c;
            color: #111827;
        }
        .priority-monitoring td {
            background: #fde047;
            color: #111827;
        }
        .priority-result {
            font-weight: 700;
        }
        .ranking-table {
            width: 100%;
            border-collapse: collapse;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            overflow: hidden;
            font-size: .88rem;
            margin-top: .4rem;
        }
        .ranking-table th,
        .ranking-table td {
            border-bottom: 1px solid #e5e7eb;
            padding: 9px 9px;
            text-align: center;
            vertical-align: middle;
        }
        .ranking-table th {
            background: #f8fafc;
            color: #475569;
            font-weight: 600;
            text-align: center;
        }
        .ranking-table tr:last-child td {
            border-bottom: none;
        }
        .ranking-table td.numeric {
            text-align: right;
            font-variant-numeric: tabular-nums;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    logo_specs = [
        ("logo_upe.jfif", "UPE", "logo-upe"),
        ("logo_upe_poli.png", "POLI", "logo-poli"),
        ("logo_ppgec.png", "PPGEC", "logo-ppgec"),
    ]
    logo_parts = []
    for file_name, label, css_class in logo_specs:
        path = asset_path(file_name)
        if path:
            logo_parts.append(f'<img class="{css_class}" src="{asset_data_uri(path)}" alt="{label}">')
        else:
            logo_parts.append(f'<span class="institutional-logo-fallback">{label}</span>')
    st.markdown(f'<div class="institutional-logos">{"".join(logo_parts)}</div>', unsafe_allow_html=True)

    st.title(APP_NAME)
    st.markdown(f'<div class="app-subtitle-small">{APP_SUBTITLE}</div>', unsafe_allow_html=True)
    st.markdown(f"**{APP_OWNER_LABEL}**")

    orcid_path = asset_path("logo_orcid.svg")
    linkedin_path = asset_path("logo_linkedin.svg")
    orcid_logo = f'<img src="{asset_data_uri(orcid_path)}" alt="ORCID">' if orcid_path else ""
    linkedin_logo = f'<img src="{asset_data_uri(linkedin_path)}" alt="LinkedIn">' if linkedin_path else ""
    st.markdown(
        f"""
        <div class="author-links">
            <a href="{ORCID_URL}" target="_blank">{orcid_logo}<span>Perfil academico</span></a>
            <a href="{LINKEDIN_URL}" target="_blank">{linkedin_logo}<span>Perfil profissional</span></a>
            <a href="{GITHUB_URL}" target="_blank"><span>Projeto no GitHub</span></a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_usage_guide() -> None:
    with st.expander("Como utilizar a plataforma", expanded=False):
        st.markdown(
            """
            1. Cadastre o projeto e o contexto da decisao.
            2. Informe as acoes, eventos, iniciativas ou projetos que precisam ser priorizados.
            3. Classifique cada item como ameaca ou oportunidade.
            4. Atribua impacto e probabilidade por escala fuzzy de 0 a 1.
            5. Gere o ranking e use a conclusao consultiva para apoiar a decisao.
            """
        )


def project_inputs() -> None:
    st.subheader("1. Projeto")
    project = st.session_state.project
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Projeto", project.get("Projeto", ""))
        organization = st.text_input("Organizacao", project.get("Organizacao", ""))
    with col2:
        responsible = st.text_input("Responsavel", project.get("Responsavel", ""))
        horizon = st.text_input("Horizonte", project.get("Horizonte", "12 meses"))
    context = st.text_area("Contexto decisorio", project.get("Contexto decisorio", ""), height=90)
    if st.button("Salvar projeto", type="primary"):
        st.session_state.project = {
            "Projeto": name,
            "Organizacao": organization,
            "Responsavel": responsible,
            "Horizonte": horizon,
            "Contexto decisorio": context,
        }
        st.success("Projeto salvo.")


def actions_inputs() -> None:
    st.subheader("2. Acoes, ameacas e oportunidades")
    st.caption("Informe uma acao por linha. A natureza, impacto e probabilidade serao ajustados na etapa seguinte.")
    count = st.number_input(
        "Quantidade de acoes",
        min_value=1,
        max_value=80,
        value=max(1, len(st.session_state.actions)),
        step=1,
    )
    existing = st.session_state.actions.copy()
    rows = []
    for index in range(int(count)):
        current = existing.iloc[index].to_dict() if index < len(existing) else {}
        action = st.text_input(
            f"Acao {index + 1}",
            current.get("Acao", f"Acao {index + 1}"),
            key=f"action_name_{index}",
        )
        rows.append(
            {
                "Acao": action,
                "Natureza": current.get("Natureza", "Ameaca"),
                "Impacto": current.get("Impacto", "Moderado"),
                "Probabilidade": current.get("Probabilidade", "Moderado"),
                "Base da informacao": current.get("Base da informacao", "Estimativa fundamentada"),
            }
        )
    if st.button("Salvar acoes", type="primary"):
        st.session_state.actions = pd.DataFrame(rows)
        st.success("Acoes salvas.")


def class_chip(classification: str) -> str:
    color = CLASS_COLORS.get(classification, "#e5e7eb")
    return f'<span class="class-chip" style="background:{color};">{classification}</span>'


def render_fuzzy_ruler() -> None:
    labels = list(FUZZY_SCALE)
    values = list(FUZZY_SCALE.values())
    ticks = "".join(
        f"<div><strong>{value:.1f}</strong><span>{label}</span></div>" for label, value in zip(labels, values)
    )
    st.markdown(
        f"""
        <style>
        .fuzzy-ruler {{
            height: 14px;
            border-radius: 999px;
            background: linear-gradient(90deg, #fee2e2 0%, #fef3c7 50%, #bbf7d0 100%);
            border: 1px solid #e5e7eb;
            margin: .2rem 0 .35rem;
        }}
        .fuzzy-ruler-ticks {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 8px;
            color: #6b7280;
            font-size: .76rem;
            margin-bottom: 1rem;
        }}
        .fuzzy-ruler-ticks strong {{
            display:block;
            color:#111827;
        }}
        .fuzzy-ruler-ticks span {{
            display:block;
        }}
        </style>
        <div class="fuzzy-ruler"></div>
        <div class="fuzzy-ruler-ticks">{ticks}</div>
        """,
        unsafe_allow_html=True,
    )


def assessment_inputs() -> None:
    st.subheader("3. Avaliacao fuzzy Impacto/Probabilidade")
    st.caption("Para ameacas, a leitura e mitigacao de risco. Para oportunidades, a leitura e captura de valor. O indice I/P usa o produto fuzzy impacto x probabilidade.")
    render_fuzzy_ruler()

    actions = st.session_state.actions.copy()
    if actions.empty:
        st.warning("Cadastre ao menos uma acao antes da avaliacao.")
        return

    header = st.columns([2.3, 1.35, 1.45, 1.45, 1.8, 1.15])
    header[0].markdown("**Acao**")
    header[1].markdown("**Natureza**")
    header[2].markdown("**Impacto**")
    header[3].markdown("**Probabilidade**")
    header[4].markdown("**Base da informacao**")
    header[5].markdown("**Indice ajustado**")

    updated_rows = []
    for index, row in actions.reset_index(drop=True).iterrows():
        current_nature = row.get("Natureza", "Ameaca")
        current_impact = row.get("Impacto", "Moderado")
        current_probability = row.get("Probabilidade", "Moderado")
        current_evidence = str(row.get("Base da informacao", "Estimativa fundamentada"))
        if current_nature not in NATURES:
            current_nature = "Ameaca"
        if current_evidence not in EVIDENCE_FACTORS:
            current_evidence = "Estimativa fundamentada"
        current_impact_value = scale_value(current_impact)
        current_probability_value = scale_value(current_probability)

        col1, col2, col3, col4, col5, col6 = st.columns([2.3, 1.35, 1.45, 1.45, 1.8, 1.15])
        action = col1.text_input("Acao", row.get("Acao", ""), key=f"assess_action_{index}", label_visibility="collapsed")
        nature = col2.selectbox(
            "Natureza",
            options=NATURES,
            index=NATURES.index(current_nature),
            key=f"assess_nature_{index}",
            label_visibility="collapsed",
        )
        impact = col3.slider(
            "Impacto",
            min_value=0.0,
            max_value=1.0,
            value=current_impact_value,
            step=0.05,
            key=f"assess_impact_{index}",
            label_visibility="collapsed",
        )
        col3.caption(f"{impact:.2f} - {fuzzy_label(impact)}")
        probability = col4.slider(
            "Probabilidade",
            min_value=0.0,
            max_value=1.0,
            value=current_probability_value,
            step=0.05,
            key=f"assess_probability_{index}",
            label_visibility="collapsed",
        )
        col4.caption(f"{probability:.2f} - {fuzzy_label(probability)}")
        evidence = col5.selectbox(
            "Base da informacao",
            options=list(EVIDENCE_FACTORS),
            index=list(EVIDENCE_FACTORS).index(current_evidence),
            key=f"assess_evidence_{index}",
            label_visibility="collapsed",
        )
        factor = EVIDENCE_FACTORS[evidence]
        col5.caption(f"fator {factor:.2f}")
        adjusted_index = ip_index(impact, probability) * factor
        col6.markdown(f'<div class="ip-box">{adjusted_index:.4f}</div>', unsafe_allow_html=True)
        updated_rows.append(
            {
                "Acao": action,
                "Natureza": nature,
                "Impacto": impact,
                "Probabilidade": probability,
                "Base da informacao": evidence,
            }
        )

    if st.button("Atualizar avaliacao", type="primary"):
        st.session_state.actions = pd.DataFrame(updated_rows)
        st.session_state.ranking = rank_actions(st.session_state.actions)
        st.success("Avaliacao atualizada e ranking recalculado.")


def render_matrix_table(title: str, matrix: dict[str, dict[str, str]], impact_order: list[str]) -> None:
    probability_order = ["Muito alto", "Alto", "Moderado", "Baixo", "Muito baixo"]
    header = "".join(f"<th>{impact}</th>" for impact in impact_order)
    rows = []
    for probability in probability_order:
        cells = []
        for impact in impact_order:
            classification = matrix[probability][impact]
            cells.append(
                f'<td style="background:{CLASS_COLORS[classification]}; font-weight:700;">{classification}</td>'
            )
        rows.append(f"<tr><th>{probability}</th>{''.join(cells)}</tr>")
    st.markdown(f"**{title}**", unsafe_allow_html=True)
    st.markdown(
        f"""
        <table class="matrix-table">
            <tr><th>Probabilidade / Impacto</th>{header}</tr>
            {''.join(rows)}
        </table>
        """,
        unsafe_allow_html=True,
    )


def matrix_reference() -> None:
    st.subheader("4. Tabela de interpretacao da prioridade")
    st.caption("Referencia para leitura gerencial do ranking. O calculo continua sendo fuzzy; a tabela resume a interpretacao esperada.")
    rows = [
        ("priority-critical", "Ameaca", "Alto", "Alta", "Risco critico", "Mitigar imediatamente"),
        ("priority-attention", "Ameaca", "Alto", "Baixa", "Risco relevante", "Monitorar e preparar contingencia"),
        ("priority-critical", "Oportunidade", "Alto", "Alta", "Oportunidade prioritaria", "Explorar rapidamente"),
        (
            "priority-attention",
            "Oportunidade",
            "Alto",
            "Baixa",
            "Oportunidade potencial",
            "Monitorar e desenvolver condicoes",
        ),
        ("priority-monitoring", "Ambos", "Baixo", "Baixa", "Monitoramento", "Acompanhar em ciclo periodico"),
    ]
    body = "".join(
        f"""
        <tr class="{css_class}">
            <td>{kind}</td>
            <td>{impact}</td>
            <td>{probability}</td>
            <td class="priority-result">{result}</td>
            <td>{recommendation}</td>
        </tr>
        """
        for css_class, kind, impact, probability, result, recommendation in rows
    )
    st.markdown(
        f"""
        <table class="reference-table">
            <thead>
                <tr>
                    <th>Tipo</th>
                    <th>Impacto</th>
                    <th>Probabilidade</th>
                    <th>Resultado</th>
                    <th>Acao recomendada</th>
                </tr>
            </thead>
            <tbody>{body}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


def priority_css_class(position: int, total: int) -> str:
    if total <= 1:
        return "priority-critical"
    ratio = position / max(total - 1, 1)
    if ratio <= 0.34:
        return "priority-critical"
    if ratio <= 0.67:
        return "priority-attention"
    return "priority-monitoring"


def priority_row_style(position: int, total: int) -> tuple[str, str]:
    css_class = priority_css_class(position, total)
    if css_class == "priority-critical":
        return "#dc2626", "#ffffff"
    if css_class == "priority-attention":
        return "#fb923c", "#111827"
    return "#fde047", "#111827"


def render_ranking_table(ranking: pd.DataFrame) -> None:
    columns = [
        "Ranking",
        "Acao",
        "Natureza",
        "Impacto",
        "Probabilidade",
        "Indice I/P",
        "Base da informacao",
        "Fator evidencia",
        "Indice ajustado",
        "Resultado",
        "Acao recomendada",
    ]
    available_columns = [column for column in columns if column in ranking.columns]
    header = "".join(f"<th>{escape(column)}</th>" for column in available_columns)
    rows = []
    numeric_columns = {"Ranking", "Indice I/P", "Fator evidencia", "Indice ajustado"}
    total_rows = len(ranking)
    for position, (_, row) in enumerate(ranking.iterrows()):
        css_class = priority_css_class(position, total_rows)
        background, text_color = priority_row_style(position, total_rows)
        cells = []
        for column in available_columns:
            value = row.get(column, "")
            align = "center"
            cells.append(
                f'<td style="background:{background}; color:{text_color}; text-align:{align};">'
                f"{escape(str(value))}</td>"
            )
        rows.append(f'<tr class="{css_class}">{"".join(cells)}</tr>')
    st.markdown(
        f"""
        <table class="ranking-table">
            <thead><tr>{header}</tr></thead>
            <tbody>{''.join(rows)}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


def ranking_outputs() -> None:
    st.subheader("5. Ranking e leitura consultiva")
    ranking = rank_actions(st.session_state.actions)
    st.session_state.ranking = ranking
    if ranking.empty:
        st.warning("Nao ha ranking calculado.")
        return

    stats = portfolio_stats(ranking)
    st.markdown(
        f"""
        <div class="metric-band">
            <div class="metric-card"><span>Acoes avaliadas</span><strong>{stats.total_actions}</strong></div>
            <div class="metric-card"><span>Ameacas</span><strong>{stats.threats}</strong></div>
            <div class="metric-card"><span>Oportunidades</span><strong>{stats.opportunities}</strong></div>
            <div class="metric-card"><span>Prioridade alta</span><strong>{stats.high_priority}</strong></div>
            <div class="metric-card"><span>Media I/P</span><strong>{stats.mean_ip_index:.4f}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_ranking_table(ranking)
    st.info(consultive_conclusion(ranking))


def export_outputs() -> None:
    st.subheader("6. Relatorio PDF")
    ranking = st.session_state.ranking if not st.session_state.ranking.empty else rank_actions(st.session_state.actions)
    data = pdf_bytes(project=st.session_state.project, actions=st.session_state.actions, ranking=ranking)
    st.download_button(
        "Baixar PDF consultivo",
        data=data,
        file_name=PDF_FILE_NAME,
        mime="application/pdf",
    )


def main() -> None:
    st.set_page_config(page_title=APP_NAME, layout="wide")
    init_state()
    render_cover()
    render_usage_guide()

    project_inputs()
    st.divider()
    actions_inputs()
    st.divider()
    assessment_inputs()
    st.divider()
    matrix_reference()
    st.divider()
    ranking_outputs()
    st.divider()
    export_outputs()


if __name__ == "__main__":
    main()
