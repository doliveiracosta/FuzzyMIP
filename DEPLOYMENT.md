# Implantacao no Streamlit Cloud

## 1. Criar o repositorio

Crie um repositorio publico no GitHub, por exemplo:

```text
FuzzyMIP
```

## 2. Enviar os arquivos

Envie para a raiz do repositorio:

- `fuzzyip_app.py`
- pasta `fuzzyip/`
- pasta `assets/`
- pasta `.streamlit/`
- `requirements.txt`
- `README.md`

## 3. Configurar no Streamlit Cloud

No Streamlit Cloud, selecione:

```text
Repository: doliveiracosta/FuzzyMIP
Branch: main
Main file path: fuzzyip_app.py
```

## 4. Publicar

Apos o deploy, o aplicativo ficara disponivel em um link publico do Streamlit.

## Observacao metodologica

O app nao possui login, banco de dados ou armazenamento permanente. As informacoes inseridas sao tratadas apenas durante a sessao de uso.

