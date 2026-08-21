"""
Gerador de fingerprint de dispositivo Android real (estilo anti-detect Dolphin Anty).
"""
from __future__ import annotations

import json
import random
import uuid

try:
    import aiograpi.config as ig_config
except Exception:
    ig_config = None

# Dispositivos reais populares com chipsets e resoluções autênticas
DEVICE_POOL: list[tuple[str, str, str, str, str, str]] = [
    ("samsung", "samsung", "SM-G991B", "o1s", "exynos2100", "1080x2400"),
    ("samsung", "samsung", "SM-G998B", "p3s", "exynos2100", "1440x3200"),
    ("samsung", "samsung", "SM-A536B", "a53x", "exynos1280", "1080x2400"),
    ("samsung", "samsung", "SM-G973F", "beyond1", "exynos9820", "1440x3040"),
    ("xiaomi", "Xiaomi", "2201117TG", "veux", "sm6375", "1080x2400"),
    ("xiaomi", "Xiaomi", "M2012K11AG", "alioth", "sm8250", "1080x2400"),
    ("xiaomi", "redmi", "22011119UY", "light", "sm6225", "1080x2400"),
    ("oneplus", "OnePlus", "LE2123", "OnePlus9", "lahaina", "1080x2400"),
    ("oneplus", "OnePlus", "KB2003", "OnePlus8T", "kona", "1080x2400"),
    ("huawei", "HUAWEI", "ANA-NX9", "HWANA", "kirin990", "1080x2340"),
    ("motorola", "motorola", "XT2141-1", "berlna", "sm4350", "1080x2400"),
    ("google", "google", "Pixel 7", "panther", "gs201", "1080x2400"),
    ("google", "google", "Pixel 8 Pro", "husky", "gs301", "1344x2992"),
    ("realme", "realme", "RMX3085", "RE54ABL1", "sm7125", "1080x2400"),
    ("oppo", "OPPO", "CPH2211", "OP4F57L1", "sm6115", "1080x2400"),
]

ANDROID = [(31, "12.0.0"), (33, "13.0.0"), (34, "14.0.0")]
LOCALES = [("pt_BR", "BR"), ("en_US", "US"), ("es_ES", "ES")]
DPI_BY_WIDTH = {720: (320, 420), 1080: (420, 480), 1344: (480, 560), 1440: (560, 640)}


def _user_agent_template() -> str:
    if ig_config is not None:
        try:
            tpl = getattr(ig_config, "USER_AGENT_BASE", None)
            if tpl:
                return tpl
        except Exception:
            pass
    return (
        "Instagram {app_version} Android ({android_version}/{android_release}; "
        "{dpi}; {resolution}; {manufacturer}; {model}; {device}; {cpu}; "
        "{locale}; {version_code})"
    )


def generate_fingerprint(seed: str | None = None) -> dict:
    rnd = random.Random()
    mfr, brand, model, device, chipset, resolution = rnd.choice(DEVICE_POOL)
    width, height = (int(x) for x in resolution.split("x"))
    dpi = rnd.choice(DPI_BY_WIDTH.get(width, [420, 480]))
    api, release = rnd.choice(ANDROID)
    locale, country = rnd.choice(LOCALES)
    tz_offset = -10800 if country == "BR" else -14400

    app_version = getattr(ig_config, "DEFAULT_APP_VERSION", "428.0.0.47.67") if ig_config else "428.0.0.47.67"
    profiles = getattr(ig_config, "APP_SETTINGS", {}) if ig_config else {}
    app_profile = profiles.get(app_version) or {}
    version_code = app_profile.get("version_code", "961145276")
    bloks_id = app_profile.get("bloks_versioning_id", "7189b949425f9bf80ea8bd880cf5a3080b292d9b1c4b38a18d112f7c4b71e7a8")

    device_fields = {
        "app_version": app_version,
        "version_code": version_code,
        "bloks_versioning_id": bloks_id,
        "android_version": api,
        "android_release": release,
        "manufacturer": mfr,
        "brand": brand,
        "model": model,
        "device": device,
        "dpi": f"{dpi}dpi",
        "resolution": resolution,
        "chipset": chipset,
        "cpu": chipset,
        "locale": locale,
    }
    try:
        user_agent = _user_agent_template().format(**device_fields)
    except KeyError:
        user_agent = ""

    uuid_seed = uuid.UUID(int=rnd.getrandbits(128), version=4)
    return {
        **device_fields,
        "country": country,
        "country_code": 55 if country == "BR" else 1,
        "timezone_offset": tz_offset,
        "user_agent": user_agent,
        "device_id": f"android-{uuid_seed.hex[:16]}",
        "uuids": {
            "uuid": str(uuid.UUID(int=rnd.getrandbits(128), version=4)),
            "phone_id": str(uuid.UUID(int=rnd.getrandbits(128), version=4)),
            "client_session_id": str(uuid.UUID(int=rnd.getrandbits(128), version=4)),
            "advertising_id": str(uuid.UUID(int=rnd.getrandbits(128), version=4)),
            "android_id": str(uuid.UUID(int=rnd.getrandbits(128), version=4)),
        },
    }


def apply_to_client(client, fingerprint: dict) -> None:
    device = {
        k: fingerprint[k]
        for k in (
            "app_version", "android_version", "android_release", "manufacturer",
            "brand", "model", "device", "dpi", "resolution", "chipset", "cpu",
        )
        if k in fingerprint
    }
    client.set_device(device)
    app_ver = fingerprint.get("app_version")
    if app_ver:
        try:
            client.set_app(app_ver)
        except Exception:
            client.set_app()
    client.set_locale(fingerprint.get("locale", "pt_BR"))
    client.set_country(fingerprint.get("country", "BR"))
    client.set_country_code(fingerprint.get("country_code", 55))
    client.set_user_agent()
    client.set_timezone_offset(fingerprint.get("timezone_offset", -10800))
    client.set_uuids(fingerprint.get("uuids") or {})


def summary(fingerprint: dict) -> dict:
    return {
        "device": f"{fingerprint.get('brand', '').title()} {fingerprint.get('model', '')}",
        "android": f"Android {fingerprint.get('android_release', '?')}",
        "screen": f"{fingerprint.get('resolution', '?')} @ {fingerprint.get('dpi', '?')}",
        "chipset": fingerprint.get("chipset", "?"),
        "locale": fingerprint.get("locale", "?"),
        "user_agent": fingerprint.get("user_agent", ""),
    }


def fingerprint_to_json(fingerprint: dict) -> str:
    return json.dumps(fingerprint, ensure_ascii=False)


def fingerprint_from_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except Exception:
        return generate_fingerprint()
