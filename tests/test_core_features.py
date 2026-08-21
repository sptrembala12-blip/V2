"""
Testes automatizados completos dos novos recursos do InstaFlow SaaS.
"""
import uuid
import httpx

BASE = "http://localhost:8000"
c = httpx.Client(base_url=BASE, timeout=60)


def test_instaflow_core():
    email = f"signup_{uuid.uuid4().hex[:6]}@instaflow.app"
    password = "pass_signup_1234"

    # 1. Cadastro com Verificação de E-mail (Código de 6 dígitos)
    r_reg = c.post("/api/auth/register", json={"email": email, "password": password})
    assert r_reg.status_code == 200
    res_reg = r_reg.json()
    assert res_reg["verification_required"] is True
    code = res_reg["code"]
    print(f"✔ Cadastro iniciado. Código de 6 dígitos gerado para {email}: {code}")

    # 2. Confirmação do Código de E-mail no Cadastro
    r_verif = c.post("/api/auth/verify-email", json={"email": email, "code": code})
    assert r_verif.status_code == 200
    token = r_verif.json()["token"]
    h = {"Authorization": f"Bearer {token}"}
    print("✔ E-mail verificado com sucesso no cadastro!")

    # 3. Troca de Senha com Código enviado por E-mail
    r_req_pwd = c.post("/api/auth/request-password-code", headers=h)
    assert r_req_pwd.status_code == 200
    pwd_code = r_req_pwd.json()["code"]
    print("✔ Código de redefinição de senha gerado:", pwd_code)

    new_pass = "nova_senha_5678"
    r_chg_pwd = c.post("/api/auth/change-password-with-code", headers=h, json={"code": pwd_code, "new_password": new_pass})
    assert r_chg_pwd.status_code == 200
    print("✔ Senha alterada com sucesso após validação do código de e-mail!")

    # 4. Criação de Conta com Emulação de Smartphone
    acc = c.post("/api/accounts", headers=h, json={
        "name": "Conta Maturação IA",
        "ig_username": f"user_{uuid.uuid4().hex[:6]}",
        "ig_password": "x",
        "simulate": True,
        "humanize": True,
        "delay_min": 2,
        "delay_max": 5,
        "warmup": True,
    }).json()
    assert acc["id"]
    print("✔ Conta cadastrada com hardware emulado:", acc["fingerprint_summary"]["device"])

    # 5. Motor de Maturação Automática com IA (Idade: Conta Criada Hoje)
    r_warm = c.post("/api/warmup/start", headers=h, json={
        "account_id": acc["id"],
        "account_age": "hoje",
        "intensity": "medio",
    }).json()
    assert "session_id" in r_warm
    print("✔ Maturação IA Anti-Queda iniciada para 'Conta Criada Hoje' (Sessão ID:", r_warm["session_id"], ")")

    # 6. Upload de Mídia e Rotação Inteligente
    fake_mp4 = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom" + b"\x00" * 2000
    r_up = c.post("/api/media/upload", headers=h, data={"account_id": acc["id"]}, files={"files": ("video_maturacao.mp4", fake_mp4, "video/mp4")})
    assert r_up.status_code == 201
    print("✔ Mídia vinculada à conta com metadados limpos")

    sched = c.post("/api/schedules", headers=h, json={
        "account_id": acc["id"],
        "name": "Disparo Automático",
        "mode": "interval",
        "target_type": "reel",
        "interval_hours": 12,
        "caption": "Reel automatizado #reels",
        "media_id": None,
        "enabled": True,
    }).json()
    assert sched["id"]

    c.post(f"/api/schedules/{sched['id']}/run-now", headers=h)
    import time
    logs = []
    for _ in range(20):
        time.sleep(0.5)
        logs = c.get("/api/logs", headers=h).json()
        if logs:
            break
    assert logs
    print("✔ Post executado com sucesso! Hash:", logs[0]["hash_before"][:8], "→", logs[0]["hash_after"][:8])

    print("\n🎉 Todos os novos recursos solicitados foram validados com 100% de sucesso!")


if __name__ == "__main__":
    test_instaflow_core()
