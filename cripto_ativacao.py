"""Criptografa os dados nominais da Ativação NPS (nomes e telefones) para publicar no site.

Mesmo esquema do SUPER DESAFIO CSAT: cada praça vira um pacote; os dados (JSON compactado com gzip) são cifrados
com AES-GCM usando uma chave aleatória; essa chave é guardada várias vezes, cada uma cifrada com uma senha
(a da praça e a geral), derivada por PBKDF2-SHA256. O navegador faz o caminho inverso com a Web Crypto API.
As senhas ficam em senhas_ativacao.json (só no computador, fora do Git).
"""
import base64
import gzip
import hashlib
import json
import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITER = 600_000
b64 = lambda b: base64.b64encode(b).decode()


def _envelope(chave, senha):
    salt, iv = os.urandom(16), os.urandom(12)
    k = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, ITER, 32)
    return {"s": b64(salt), "i": b64(iv), "c": b64(AESGCM(k).encrypt(iv, chave, None))}


def pacote(dados, senhas):
    chave, iv = AESGCM.generate_key(256), os.urandom(12)
    bruto = gzip.compress(json.dumps(dados, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    return {"i": b64(iv), "c": b64(AESGCM(chave).encrypt(iv, bruto, None)),
            "k": [_envelope(chave, s) for s in senhas if s]}


def senhas_locais(pasta, pracas):
    """Lê (ou cria) senhas_ativacao.json com uma senha por praça e uma geral. Nunca vai para o Git."""
    arq = os.path.join(pasta, "senhas_ativacao.json")
    senhas = json.load(open(arq, encoding="utf-8")) if os.path.exists(arq) else {}
    novas = [k for k in list(pracas) + ["geral"] if not senhas.get(k)]
    for k in novas:
        senhas[k] = secrets.token_urlsafe(9)
    if novas or "_leia" not in senhas:
        senhas["_leia"] = "Senhas da Ativação NPS: uma por praça e a geral (abre todas). Não publicar."
        with open(arq, "w", encoding="utf-8") as f:
            json.dump(senhas, f, ensure_ascii=False, indent=2)
        print("ativação: senhas criadas em senhas_ativacao.json para:", ", ".join(novas))
    return senhas


def gravar(pasta, pacotes):
    """pacotes: {"SAO-LUIS": {dados da praça}, ...}. Grava ativacao_cripto.js."""
    if not pacotes:
        print("ativação: nada para publicar")
        return
    senhas = senhas_locais(pasta, pacotes)
    saida = {"iter": ITER, "pracas": {p: pacote(d, [senhas.get(p), senhas.get("geral")]) for p, d in pacotes.items()}}
    with open(os.path.join(pasta, "ativacao_cripto.js"), "w", encoding="utf-8") as f:
        f.write("// Gerado por atualizar_dados.py - dados nominais da Ativação CRIPTOGRAFADOS (AES-GCM + PBKDF2)\n")
        f.write("window.ATIV_CRIPTO = ")
        json.dump(saida, f, separators=(",", ":"))
        f.write(";\n")
    print("ativação: ativacao_cripto.js gravado (" + ", ".join(f"{p}: {len(d['pedidos'])} pedidos" for p, d in pacotes.items()) + ")")
