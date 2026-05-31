"""Constants for the FuzzyMIP prioritization app."""

APP_NAME = "FuzzyMIP Prioritizer"
APP_SUBTITLE = "Logica Fuzzy e Matriz de Impacto e Probabilidade gerando acoes prioritarias."
APP_OWNER = "David de Oliveira Costa"
APP_OWNER_LABEL = f"Desenvolvido por {APP_OWNER}, Doutorando em Engenharia de Computacao, 2026."

ORCID_URL = "https://orcid.org/0000-0002-6138-7451"
LINKEDIN_URL = "https://linkedin.com/in/daviddeoliveiracosta"
GITHUB_URL = "https://github.com/doliveiracosta"

NATURES = ["Ameaca", "Oportunidade"]

FUZZY_SCALE = {
    "Muito baixo": 0.10,
    "Baixo": 0.30,
    "Moderado": 0.50,
    "Alto": 0.70,
    "Muito alto": 0.90,
}

CLASS_COLORS = {
    "Alta": "#fb7185",
    "Media": "#fde68a",
    "Baixa": "#a9d18e",
}

CLASS_ORDER = {
    "Alta": 3,
    "Media": 2,
    "Baixa": 1,
}

EVIDENCE_FACTORS = {
    "Dado real / mensurado": 1.00,
    "Estimativa fundamentada": 0.85,
    "Percepcao preliminar": 0.70,
    "Baixa evidencia": 0.55,
}

PDF_FILE_NAME = "relatorio_consultivo_fuzzymip.pdf"
