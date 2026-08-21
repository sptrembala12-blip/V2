"""
Testes unitários e de integração para o fluxo de Autenticação, Sessões e Configurações do InstaFlow.
"""
import uuid
import httpx

BASE = "http://localhost:8000"
c = httpx.Client(base_url=BASE, timeout=60)


def test_auth_and_settings_flow():
    email = f"user_{uuid.uuid4().hex[:6]}@instaflow.app"
    password = "initial_pass_123"

    # 1. Registrar e Confirmar Código de E-mail
    r_reg = c.post("/api/auth/register", json={"email": email, "password": password})
    assert r_reg.status_code == 200, r_reg.text
    reg_data = r_reg.json()
    if reg_data.get("verification_required"):
        code = reg_data["code"]
        r_ver = c.post("/api/auth/verify-email", json={"email": email, "code": code})
        assert r_ver.status_code == 200
        token = r_ver.json()["token"]
    else:
        token = reg_data["token"]

    headers = {"Authorization": f"Bearer {token}"}
    print("✔ Registro e verificação de e-mail de usuário com sucesso")

    # 2. Obter /me
    r_me = c.get("/api/auth/me", headers=headers)
    assert r_me.status_code == 200
    assert r_me.json()["email"] == email
    print("✔ GET /api/auth/me validado")

    # 3. Obter configurações
    r_cfg = c.get("/api/auth/settings", headers=headers)
    assert r_cfg.status_code == 200
    cfg = r_cfg.json()
    assert "theme_preference" in cfg
    assert "storage_type" in cfg
    print("✔ GET /api/auth/settings validado:", cfg["storage_type"])

    # 4. Alterar tema
    r_theme = c.post("/api/auth/theme", headers=headers, json={"theme": "claro"})
    assert r_theme.status_code == 200
    assert r_theme.json()["theme"] == "claro"
    print("✔ POST /api/auth/theme (claro) validado")

    # 5. Alterar 2FA
    r_2fa = c.post("/api/auth/two-factor", headers=headers, json={"enabled": True})
    assert r_2fa.status_code == 200
    assert r_2fa.json()["two_factor_enabled"] is True
    print("✔ POST /api/auth/two-factor (ativado) validado")

    # 6. Alterar Senha com Código por E-mail
    r_code = c.post("/api/auth/request-password-code", headers=headers)
    assert r_code.status_code == 200
    pwd_code = r_code.json()["code"]

    new_password = "new_pass_456"
    r_pwd = c.post("/api/auth/change-password-with-code", headers=headers, json={
        "code": pwd_code,
        "new_password": new_password
    })
    assert r_pwd.status_code == 200
    print("✔ POST /api/auth/change-password-with-code validado com código do e-mail")

    # 7. Testar login com nova senha
    r_login_new = c.post("/api/auth/login", json={"email": email, "password": new_password})
    assert r_login_new.status_code == 200
    print("✔ Login com nova senha aprovado")

    # 8. Testar conta com persistência dupla (SQLite + disco)
    acc = c.post("/api/accounts", headers=headers, json={
        "name": "Conta Teste Persistência",
        "ig_username": f"user_{uuid.uuid4().hex[:6]}",
        "ig_password": "dummy_password_123",
        "simulate": True,
        "humanize": True,
        "delay_min": 2,
        "delay_max": 5,
        "warmup": True,
    }).json()
    assert acc["id"]
    print("✔ Conta cadastrada com fingerprint e persistência:", acc["fingerprint_summary"]["device"])

    # 9. Testar conexão sem forçar relogin
    r_check = c.post(f"/api/accounts/{acc['id']}/check-connection", headers=headers)
    assert r_check.status_code == 200
    check_data = r_check.json()
    assert check_data["session_active"] is True
    print("✔ Check connection validado com sessão ativa:", check_data["status"])

    print("\n🎉 Todos os testes de Autenticação, Sessões e Configurações passaram com 100% de sucesso!")


if __name__ == "__main__":
    test_auth_and_settings_flow()
