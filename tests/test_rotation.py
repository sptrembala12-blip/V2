"""
Teste do motor de rotação de mídias do InstaFlow.
"""
import uuid
import httpx

BASE = "http://localhost:8000"
c = httpx.Client(base_url=BASE, timeout=60)


def test_media_rotation_flow():
    email = f"rot_{uuid.uuid4().hex[:6]}@instaflow.app"
    password = "pass1234rotation"

    # 1. Registra usuário e valida código
    r = c.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code == 200
    reg_js = r.json()
    if reg_js.get("verification_required"):
        code = reg_js["code"]
        r_v = c.post("/api/auth/verify-email", json={"email": email, "code": code})
        assert r_v.status_code == 200
        token = r_v.json()["token"]
    else:
        token = reg_js["token"]
    h = {"Authorization": f"Bearer {token}"}

    # 2. Cria conta de simulação
    acc = c.post("/api/accounts", headers=h, json={
        "name": "Conta Rotação",
        "ig_username": "rotacao.teste",
        "ig_password": "x",
        "simulate": True,
    }).json()

    # 3. Envia 5 vídeos simulados
    video_ids = []
    fake_mp4 = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom" + b"\x00" * 2000
    for i in range(1, 6):
        r_up = c.post("/api/media/upload", headers=h, files={"files": (f"video_{i}.mp4", fake_mp4, "video/mp4")})
        assert r_up.status_code == 201
        created = r_up.json()["created"][0]
        video_ids.append(created["id"])
    print(f"✔ 5 vídeos enviados com IDs: {video_ids}")

    # 4. Executa 5 postagens em modo rotação automática (media_id = None)
    posted_media_ids = []
    for step in range(1, 6):
        c.post("/api/posting/now", headers=h, json={
            "account_id": acc["id"],
            "media_id": None,
            "target_type": "reel",
            "caption": f"Post automático #{step}",
        })
        import time
        for _ in range(30):
            time.sleep(0.5)
            logs = c.get("/api/logs", headers=h).json()
            if len(logs) == step:
                break
        assert len(logs) == step
        last_log = logs[0]
        posted_media_ids.append(last_log["media_id"])
        print(f"✔ Post #{step} utilizou a mídia ID {last_log['media_id']} ({last_log['media_name']})")

    # Verifica se todos os 5 vídeos diferentes foram utilizados na primeira rodada
    assert set(posted_media_ids) == set(video_ids), "Nem todos os vídeos foram postados!"
    print("✔ Todos os 5 vídeos foram postados exatamente 1 vez cada!")

    # 5. Executa o 6º post para verificar a finalização automática da fila (sem repetição indevida)
    c.post("/api/posting/now", headers=h, json={
        "account_id": acc["id"],
        "media_id": None,
        "target_type": "reel",
        "caption": "Post #6 tentativa",
    })
    for _ in range(30):
        time.sleep(0.5)
        logs = c.get("/api/logs", headers=h).json()
        if len(logs) == 6:
            break
    assert len(logs) == 6
    last_action = logs[0]["action"]
    assert "concluida" in last_action or "finalizada" in last_action
    print(f"✔ Post #6 finalizou a fila com sucesso: '{logs[0]['message']}'")

    print("\n🎉 Teste de Fila & Rotação Sem Repetição Aprovado com 100% de Sucesso!")


if __name__ == "__main__":
    test_media_rotation_flow()
