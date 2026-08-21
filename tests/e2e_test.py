"""
Teste E2E completo do InstaFlow SaaS.
"""
import io
import sys
import time
import uuid
import concurrent.futures as cf

import httpx
from PIL import Image

def test_full_e2e():
    BASE = "http://localhost:8000"
    c = httpx.Client(base_url=BASE, timeout=90)

    email = f"teste-{uuid.uuid4().hex[:8]}@instaflow.app"
    password = "teste1234"

    # 1) frontend + health
    r = c.get("/")
    assert r.status_code == 200 and "InstaFlow" in r.text
    print("✔ GET / → HTML do SaaS")
    print("✔ health:", c.get("/api/health").json())

    # 2) registrar usuário novo e verificar e-mail
    r = c.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    reg_js = r.json()
    if reg_js.get("verification_required"):
        code = reg_js["code"]
        r_v = c.post("/api/auth/verify-email", json={"email": email, "code": code})
        assert r_v.status_code == 200
        token = r_v.json()["token"]
    else:
        token = reg_js["token"]

    h = {"Authorization": f"Bearer {token}"}
    print("✔ registro e verificação de e-mail:", email)

    # 3) senha errada → 401
    r = c.post("/api/auth/login", json={"email": email, "password": "errada123"})
    assert r.status_code == 401
    print("✔ senha errada → 401")

    # 4) conta em simulação para pipeline
    acc_sim = c.post("/api/accounts", headers=h, json={
        "name": "Conta Simulação", "ig_username": "sim.teste", "ig_password": "x",
        "simulate": True, "humanize": True, "delay_min": 2, "delay_max": 5, "warmup": True}).json()
    print("✔ conta simulação criada | fingerprint:", acc_sim["fingerprint_summary"]["device"])

    # 5) upload de imagem com EXIF
    img = Image.new("RGB", (800, 600), (90, 120, 200))
    buf = io.BytesIO()
    exif = Image.Exif()
    exif[0x0131] = "SOFTWARE TEST"
    img.save(buf, format="JPEG", quality=95, exif=exif)
    r = c.post("/api/media/upload", headers=h, files={"files": ("foto_teste.jpg", buf.getvalue(), "image/jpeg")})
    assert r.status_code == 201, r.text
    photo = r.json()["created"][0]
    print("✔ foto enviada, metadados limpos:", photo["metadata_clean"])

    # 6) vídeo
    fake_mp4 = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom" + b"\x00" * 5000
    r = c.post("/api/media/upload", headers=h, files={"files": ("video_teste.mp4", fake_mp4, "video/mp4")})
    assert r.status_code == 201, r.text
    video = r.json()["created"][0]
    print("✔ vídeo enviado | kind:", video["kind"], "| limpo:", video["metadata_clean"])

    # 7) agendamento e execução imediata
    s1 = c.post("/api/schedules", headers=h, json={
        "account_id": acc_sim["id"], "name": "A cada 24h", "mode": "interval", "target_type": "reel",
        "interval_hours": 24, "caption": "Legenda teste", "jitter_min": 0, "enabled": True}).json()
    assert s1["next_run_at"]
    print("✔ agendamento criado:", s1["name"])

    assert c.post(f"/api/schedules/{s1['id']}/run-now", headers=h).status_code == 200
    for _ in range(20):
        time.sleep(1)
        logs = c.get("/api/logs", headers=h).json()
        if logs:
            break
    assert logs
    lg = logs[0]
    print("✔ post executado:", lg["action"], "| hash:", lg["hash_before"][:10], "→", lg["hash_after"][:10])

    # 8) teste do motor de aquecimento
    r_warmup = c.post("/api/warmup/start", headers=h, json={
        "account_id": acc_sim["id"], "niche": "cortes de anime, animesbrasil", "intensity": "leve",
        "watch_reels": True, "like_posts": True, "follow_profiles": False, "explore_tab": True}).json()
    assert "session_id" in r_warmup
    print("✔ motor de aquecimento iniciado:", r_warmup["session_id"])

    print("\n🎉 E2E completo com sucesso!")

if __name__ == "__main__":
    test_full_e2e()
