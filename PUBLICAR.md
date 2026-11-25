# Publicar o NPS Clique e Retire no GitHub Pages

A cada `push` na `main`, o GitHub Actions (`.github/workflows/pages.yml`) publica `index.html`, `dados.js`, `ativacao_cripto.js` e `planilha.js`.

> O site é **público**: qualquer pessoa com o link vê as contagens por loja. Nomes e telefones só abrem com a senha da praça (ou a geral), que ficam em `senhas_ativacao.json`, no computador, fora do Git. Troque as senhas apagando o arquivo e rodando o script de novo (gera novas e recriptografa).

## Configuração única
1. Crie o repositório no GitHub e envie esta pasta (`git init`, `git add .`, `git commit`, `git remote add origin ...`, `git push -u origin main`). O `.gitignore` já deixa de fora as planilhas e as senhas.
2. No GitHub, abra o repositório > **Settings > Pages** > em **Source**, escolha **GitHub Actions**.
3. Envie as senhas de cada praça para quem vai operar (por canal seguro, não pelo repositório).

## Dia a dia: atualizar os dados
1. Salve a nova exportação do NPS em `base_nps/` e a base de pedidos em `Base_Pedidos_Clique&Retire/`.
2. Rode:
   ```
   python atualizar_dados.py
   ```
3. Envie:
   ```
   git add dados.js ativacao_cripto.js
   git commit -m "Dados até DD/MM"
   git push
   ```
4. Em 1 a 2 minutos o site atualiza.

Se as marcações de "acionado" precisam ser vistas por toda a equipe, configure a planilha compartilhada abaixo; sem ela, cada pessoa vê só as marcações do próprio navegador.

## Planilha compartilhada de acionamentos (opcional)
Usa o mesmo protocolo do SUPER DESAFIO CSAT: o Apps Script recebe `op: acionamento` e devolve `tipo=acionamentos`. O script atual do PULSAR grava na aba `acionamentos_csat`; para o NPS é preciso uma aba própria (ex.: `acionamentos_nps`) tratando `ciclo = nps-clique-retire`. Depois, em GitHub > Settings > Secrets and variables > Actions, crie os segredos `NPS_PLANILHA_URL` e `NPS_PLANILHA_CHAVE`; a publicação coloca os valores no `planilha.js` do site. Sem os segredos a publicação segue normalmente, com os contatos só no navegador.
