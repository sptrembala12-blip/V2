# InstaFlow — SaaS de Automação & Maturação para Instagram

Sistema profissional de automação, postagens inteligentes, rotação de mídias sem repetição e maturação autônoma 24/7 com IA por geolocalização para Instagram. Desenvolvido com FastAPI, SQLAlchemy 2.0, APScheduler, aiograpi (fork assíncrono do instagrapi) e frontend SPA/PWA responsivo com design iOS 26 Glassmorphism.

---

## Principais Funcionalidades

- **Design iOS 26 Glassmorphism & PWA**:
  - Interface com visual translúcido, blur dinâmico, modos Claro, Escuro e Automático.
  - Totalmente livre de emojis — ícones vetoriais SVG nítidos e padronizados.
  - Drawer retrátil com detecção de hover na borda esquerda no desktop e menu touch responsivo no mobile.
  - Suporte a instalação como App PWA no iPhone (Safari) e Android (Chrome).

- **Autenticação Real & Dupla Persistência**:
  - Login direto por Usuário e Senha com emulação de hardware Android real (marca, modelo, GPU, DPI).
  - Suporte a autenticação em dois fatores (2FA) e tratamento inteligente de checkpoints.
  - Importação rápida via Cookie `sessionid` com proteção contra loops de redirecionamento.
  - Dupla persistência: sessões salvas em disco e gravadas no banco de dados (resiliente a reinicializações no Render).

- **Gestão & Validação de Proxies**:
  - Suporte nativo ao formato comercial `IP:PORTA:USUARIO:SENHA` com conversão automática.
  - Teste de conexão em tempo real com medição de latência e verificação de IP de saída.

- **Pipeline de Mídias com Qualidade Máxima & Anti-Detecção**:
  - Upload em lote de mais de 200 fotos e vídeos com barra de progresso em tempo real.
  - Remoção de metadados EXIF/ICC sem perda de qualidade.
  - Processamento de vídeo via FFmpeg em modo cópia direta (`-c copy`), preservando 100% da resolução e bitrate original (padrão iPhone Pro Max).
  - Re-Hash Criptográfico: geração de SHA-256 exclusivo por postagem através da injeção de atom `free` ISO MP4 sem alterar a integridade do arquivo.
  - Streaming de vídeo com suporte a HTTP 206 (Range Requests) para reprodução instantânea em qualquer dispositivo.

- **Fila de Publicações & Rotação Inteligente**:
  - Disparo de Reels, Reels de Teste (*Trial Reels* com flag prioritária para não-seguidores), Stories e Fotos no Feed.
  - Rotação com término automático: ao postar o último item da lista, finaliza o ciclo e desativa o agendamento sem repetições indevidas.
  - Botões para resetar o status de envio em lote ou excluir todas as mídias da biblioteca.

- **Maturação Autônoma 24/7 com IA por País**:
  - Ciclos de 3 dias (72h) com navegação humanizada, retenção de visualização de 10 a 25s e curtidas orgânicas.
  - Intervalos de descanso realistas (45 a 120 minutos) entre sessões com reabertura programada.
  - Segmentação regional em 11 países: Brasil, Estados Unidos, Portugal, Espanha, Reino Unido, México, França, Alemanha, Itália, Argentina e Global.
  - Gerenciamento multi-contas simultâneo com controles de Pausar e Retomar dedicados por conta.

---

## Como Rodar Localmente

### Pré-requisitos
- Python 3.10 ou superior
- FFmpeg instalado no sistema (ou o pacote instalará automaticamente via `imageio-ffmpeg`)

### No Windows:
1. Dê dois cliques em `iniciar.bat` para iniciar o servidor local na porta 8000.
2. Dê dois cliques em `gerar_link_publico.bat` para criar um túnel HTTPS seguro e acessar pelo celular.

### No Linux / macOS:
```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Inicie o servidor
python3 run.py
```
Acesse no navegador: `http://localhost:8000`

---

## Como Fazer Deploy no Render.com (Nuvem)

1. Crie uma conta em [render.com](https://render.com).
2. Conecte seu repositório do GitHub contendo este código.
3. Crie um **Web Service**:
   - **Environment**: `Python 3` ou `Docker`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
4. *(Opcional)* Para persistência permanente mesmo em contas gratuitas, crie um banco **PostgreSQL** no Render e adicione a variável de ambiente:
   - `DATABASE_URL`: `postgres://...`
5. Adicione as variáveis de ambiente (veja `.env.example` para a lista completa):
   - `ENVIRONMENT`: `production` (ativa CORS restrito, esconde /docs, exige SECRET_KEY)
   - `SECRET_KEY`: valor longo e aleatório — **essencial** para não perder as credenciais criptografadas entre deploys (gere com `python -c "import secrets; print(secrets.token_urlsafe(48))"`)
   - `CORS_ORIGINS`: `https://seudominio.com` (domínios permitidos)
   - `APP_TZ`: `America/Sao_Paulo`
   - `PORT`: `8000`
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`: (para disparo de e-mails reais de recuperação/ativação).

### Variáveis de configuração (resumo)

Todas têm defaults seguros e são documentadas em `.env.example`. Destaques:

| Variável | Padrão | Função |
|----------|--------|--------|
| `SECRET_KEY` | (efêmera) | Chave mestra de criptografia — defina em produção |
| `SESSION_TTL_DAYS` | `30` | Expiração da sessão de login |
| `MIN_PASSWORD_LENGTH` | `8` | Política de senha do painel |
| `LOGIN_MAX_ATTEMPTS` / `LOGIN_LOCKOUT_MINUTES` | `8` / `15` | Anti-força-bruta no login |
| `ALLOW_LOGIN_AUTOCREATE` | `false` | Criar conta no 1º login (opt-in) |
| `MAX_POSTS_PER_DAY` | `25` | Limite anti-ban por conta (24h) |
| `NETWORK_RETRY_ATTEMPTS` | `3` | Retentativas em falha de rede |
| `LOG_RETENTION_DAYS` | `90` | Limpeza automática de logs |
| `ACCOUNT_HEALTHCHECK_MINUTES` | `0` | Health-check periódico de contas |

---

## Estrutura do Projeto

```text
instaflow/
├── app/
│   ├── config.py              # Configurações centrais e diretórios
│   ├── database.py            # Conexão SQLAlchemy com SQLite / PostgreSQL
│   ├── models.py              # Modelos de dados (User, Account, Media, Schedule, etc.)
│   ├── schemas.py             # Validações Pydantic e normalizadores
│   ├── security.py            # Hash scrypt, criptografia Fernet e política de senha
│   ├── instagram_service.py   # Gerenciador de sessões aiograpi e 2FA
│   ├── media.py               # Limpeza EXIF, thumbnails e re-hash criptográfico
│   ├── posting.py             # Pipeline de publicação multi-formato
│   ├── warmup.py              # Motor de maturação 24/7 com IA por país
│   ├── scheduler.py           # Agendador APScheduler + manutenção (logs, health-check)
│   ├── email_service.py       # Envio de e-mails via SMTP
│   ├── retry_util.py          # Retry com backoff em falhas de rede
│   ├── aiograpi_bridge.py     # Ponte síncrona para o aiograpi (async)
│   └── routers/               # Rotas modulares da API REST
├── static/
│   ├── index.html             # Interface SPA moderna estilo iOS 26
│   ├── css/style.css          # Design Glassmorphism e responsividade
│   ├── js/app.js              # Controlador do frontend e requisições
│   └── sw.js                  # Service Worker PWA (Network-First)
├── tests/                     # Bateria de testes automatizados E2E e unitários
├── Dockerfile                 # Configuração para containers Docker
├── render.yaml                # Manifesto de infraestrutura para o Render
└── requirements.txt           # Dependências do projeto
```

---

## Licença
InstaFlow SaaS — Todos os direitos reservados.
