# clockapp — Deploy no Railway (guia rápido)

Este repositório contém o projeto **clockapp** (Flask + MySQL) pronto para deploy no Railway.

## Arquivos importantes
- `app.py` — aplicação Flask
- `requirements.txt` — dependências
- `schema.sql` — script para criar as tabelas
- `Procfile` — comando de start para Railway (gunicorn)
- `.env.example` — exemplo de variáveis de ambiente (não coloque senhas reais neste arquivo)
- `templates/` — templates HTML
- `static/` — CSS básico
- `.gitignore` — ignora venv, .env, etc.

## Passo a passo resumido
1. Crie um repositório no GitHub e faça push deste código (não suba `.env`).
2. No Railway, clique em **New Project → Deploy from GitHub repo** e conecte seu repositório.
3. Crie um serviço de banco **MySQL** no mesmo projeto (Railway → New → Database → MySQL).
4. Vá em **Variables** (do serviço web) e adicione as variáveis de ambiente:
   - DB_HOST (host fornecido pelo serviço MySQL)
   - DB_USER (normalmente `root`)
   - DB_PASS (senha fornecida pelo Railway)
   - DB_NAME (normalmente `railway` ou `clockdb`)
   - FLASK_SECRET (qualquer chave aleatória)
   - ADMIN_USER (ex: admin)
   - ADMIN_PASS (ex: admin123)
5. Deploy: Railway instalará dependências e iniciará o serviço (gunicorn).
6. Depois que o serviço estiver rodando, abra o **Database Manager** do MySQL e execute o `schema.sql` para criar as tabelas.
7. Use a aplicação pública disponibilizada pela Railway.

## Notas
- Não suba o arquivo `.env` com senhas. Use as _Environment Variables_ do Railway.
- O arquivo `.env.example` mostra quais variáveis configurar.
- Em produção, implemente autenticação segura (este exemplo usa `?auth=1` para simplicidade).
