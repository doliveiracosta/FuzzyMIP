# FuzzyMIP Prioritizer

Plataforma computacional para priorizacao fuzzy de acoes estrategicas, combinando logica fuzzy e matriz de Impacto e Probabilidade.

## Proposito

O FuzzyMIP Prioritizer apoia a classificacao e o ranqueamento de acoes, ameacas e oportunidades a partir de tres componentes:

- impacto fuzzy no negocio;
- probabilidade fuzzy de ocorrencia;
- qualidade da evidencia utilizada na avaliacao.

O indice principal e calculado por:

```text
Indice I/P = Impacto fuzzy x Probabilidade fuzzy
Indice ajustado = Indice I/P x Fator de evidencia
```

## Estrutura metodologica

A ferramenta separa a leitura decisoria de ameacas e oportunidades:

- ameacas sao interpretadas como risco e orientam acoes de mitigacao;
- oportunidades sao interpretadas como potencial estrategico e orientam acoes de captura de valor.

Para evitar falsa precisao, o usuario informa a base da avaliacao:

- dado real / mensurado;
- estimativa fundamentada;
- percepcao preliminar;
- baixa evidencia.

Essa informacao aplica um fator de abatimento ao indice, permitindo que avaliacoes pouco sustentadas nao tenham o mesmo peso de dados mensurados.

## Como executar localmente

```bash
pip install -r requirements.txt
streamlit run fuzzyip_app.py
```

## Arquivos principais

- `fuzzyip_app.py`: interface Streamlit.
- `fuzzyip/core.py`: calculos fuzzy, ranking e estatisticas.
- `fuzzyip/report.py`: geracao do relatorio PDF.
- `assets/`: logomarcas institucionais e links de perfil.

## Autor

Desenvolvido por David de Oliveira Costa, Doutorando em Engenharia de Computacao, 2026.

