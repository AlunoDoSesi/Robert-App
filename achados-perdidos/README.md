# AchaAí — Achados e Perdidos

Mural colaborativo de achados e perdidos construído com **Python, Flask, SQLite, HTML, CSS e JavaScript**. A interface usa uma paleta violeta acolhedora, componentes responsivos e mensagens claras para tornar o cadastro e a busca rápidos em qualquer tela.

## Recursos

- Cadastro de itens **perdidos** ou **encontrados**;
- Campos para nome, descrição, local e contato;
- Upload opcional de imagem (PNG, JPG, GIF ou WEBP, até 5 MB);
- Visualização dos itens em cards, com destaque para avisos ativos;
- Filtros por **Todos**, **Perdidos** e **Encontrados**;
- Busca por palavra-chave em nome, descrição, local e contato;
- Marcação como **Resolvido** e opção de reabrir o aviso;
- Mensagens de feedback após cadastro, resolução e validações;
- Banco SQLite criado automaticamente na primeira execução;
- Layout responsivo com HTML semântico, CSS próprio e JavaScript leve;
- Testes automatizados das rotas principais.

## Como executar

> Requer Python 3.10 ou superior.

```bash
# 1. Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Iniciar a aplicação
python app.py
```

Abra `http://127.0.0.1:5000` no navegador.

### Variáveis opcionais

```bash
export SECRET_KEY="uma-chave-segura"
export PORT=5000
export FLASK_DEBUG=1
```

O arquivo SQLite é criado em `data/achados.db` e as imagens são salvas em `static/uploads/`.

## Testes

```bash
pytest -q
```

## Estrutura

```text
achados-perdidos/
├── app.py                  # Rotas Flask, persistência e validações
├── data/                   # Banco SQLite gerado localmente
├── requirements.txt
├── static/
│   ├── css/styles.css      # Design system e layout responsivo
│   ├── js/app.js           # Preview de imagem e microinterações
│   └── uploads/            # Imagens enviadas pelos usuários
├── templates/
│   ├── base.html
│   ├── form.html
│   └── index.html
└── tests/test_app.py
```

## Decisões de UI/UX

A experiência foi desenhada com a ideia de um **mural acolhedor e confiável**: violeta profundo para navegação e contraste, lilás para superfícies suaves, verde menta para itens resolvidos e âmbar para avisos encontrados. O fluxo principal privilegia a leitura rápida dos cards, filtros visíveis e um CTA destacado para publicar um novo aviso.

## Próximos passos sugeridos

Para publicar em produção, configure uma `SECRET_KEY` própria, use armazenamento persistente para uploads e avalie autenticação/moderação antes de abrir o mural para uma comunidade maior.
