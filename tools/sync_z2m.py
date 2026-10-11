#!/usr/bin/env python3
"""Upstream Zigbee2MQTT add-on'undan her instance için bir z2m_<id>/ klasörü üretir.

Kullanım:
    python tools/sync_z2m.py            # üret / güncelle
    python tools/sync_z2m.py --check    # sadece kontrol: değişiklik varsa exit 1
    python tools/sync_z2m.py --prune    # instances.yaml'da olmayan z2m_* klasörlerini de sil

Upstream config.json olduğu gibi kopyalanır; sadece slug, name, url, description,
options.data_path ve 8485/tcp host portu değiştirilir. version ve image ASLA değişmez:
Supervisor imajı ghcr.io/zigbee2mqtt/zigbee2mqtt-{arch}:<version> olarak çeker.
"""

import argparse
import copy
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path

import yaml

UPSTREAM_RAW = "https://raw.githubusercontent.com/zigbee2mqtt/hassio-zigbee2mqtt/master/zigbee2mqtt/"
UPSTREAM_FILES = ["config.json", "icon.png", "logo.png", "DOCS.md", "CHANGELOG.md"]
OWN_REPO_URL = "https://github.com/homtreltd/mitas-zigbee2mqtt-addons"
SLUG_PREFIX = "z2m_"
SOCAT_CONTAINER_PORT = "8485/tcp"
DONGLE_TCP_PORT = 6638  # Sonoff Dongle Max TCP serial portu
DONGLE_ADAPTER = "ember"
DONGLE_BAUDRATE = 115200

ROOT = Path(__file__).resolve().parent.parent
ID_RE = re.compile(r"^[a-z0-9_]+$")


def fetch(name: str) -> bytes:
    with urllib.request.urlopen(UPSTREAM_RAW + name, timeout=30) as resp:
        return resp.read()


def load_instances() -> list[dict]:
    data = yaml.safe_load((ROOT / "instances.yaml").read_text(encoding="utf-8"))
    instances = data["instances"]
    errors = []
    checks = {
        "id": lambda i: str(i.get("id")),
        "data_path": lambda i: str(i.get("data_path")),
        "socat_port": lambda i: str(i.get("socat_port")),
        "base_topic": lambda i: base_topic(i) if i.get("data_path") else "",
        "dongle_ip": lambda i: str(i.get("dongle_ip") or f"<boş:{i.get('id')}>"),
    }
    for field, get in checks.items():
        values = [get(i) for i in instances]
        dupes = {v for v in values if values.count(v) > 1}
        if dupes:
            errors.append(f"tekrarlanan {field}: {', '.join(sorted(dupes))}")
    for i in instances:
        if not ID_RE.match(str(i.get("id", ""))):
            errors.append(f"geçersiz id (sadece a-z, 0-9, _): {i.get('id')!r}")
        if not str(i.get("data_path", "")).startswith("/config/") or i["data_path"].rstrip("/") == "/config":
            errors.append(f"geçersiz data_path: {i.get('id')}: {i.get('data_path')!r}")
        if not i.get("name"):
            errors.append(f"name boş: {i.get('id')}")
    if errors:
        sys.exit("instances.yaml hatalı:\n  " + "\n  ".join(errors))
    return instances


def build_config(upstream: dict, inst: dict) -> dict:
    cfg = copy.deepcopy(upstream)
    cfg["slug"] = SLUG_PREFIX + inst["id"]
    cfg["name"] = inst["name"]
    cfg["url"] = OWN_REPO_URL
    ip = inst.get("dongle_ip")
    cfg["description"] = upstream["description"] + (f" — dongle {ip}" if ip else "")
    cfg["options"]["data_path"] = inst["data_path"]
    # Sadece base_topic: server/user/password boş kalınca add-on bunları Supervisor'ın
    # Mosquitto servisinden alır. Şifre public repoya asla yazılmaz.
    cfg["options"]["mqtt"] = {"base_topic": base_topic(inst)}
    if ip:
        cfg["options"]["serial"] = {
            "port": f"tcp://{ip}:{DONGLE_TCP_PORT}",
            "adapter": DONGLE_ADAPTER,
            "baudrate": DONGLE_BAUDRATE,
        }
    cfg.setdefault("ports", {})[SOCAT_CONTAINER_PORT] = int(inst["socat_port"])
    return cfg


def base_topic(inst: dict) -> str:
    return inst.get("base_topic") or inst["data_path"].rstrip("/").rsplit("/", 1)[-1]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows konsolunda Türkçe karakterler bozulmasın
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="dosya yazma, değişiklik varsa exit 1")
    parser.add_argument("--prune", action="store_true", help="listede olmayan z2m_* klasörlerini sil")
    args = parser.parse_args()

    instances = load_instances()
    files = {name: fetch(name) for name in UPSTREAM_FILES}
    upstream = json.loads(files["config.json"])
    new_version = upstream["version"]

    changed: list[str] = []
    old_versions: set[str] = set()

    for inst in instances:
        folder = ROOT / (SLUG_PREFIX + inst["id"])
        cfg_path = folder / "config.json"
        if cfg_path.exists():
            old_versions.add(json.loads(cfg_path.read_text(encoding="utf-8"))["version"])

        wanted = dict(files)
        wanted["config.json"] = (
            json.dumps(build_config(upstream, inst), indent=2, ensure_ascii=False) + "\n"
        ).encode("utf-8")

        for name, content in wanted.items():
            path = folder / name
            if path.exists() and path.read_bytes() == content:
                continue
            changed.append(f"{folder.name}/{name}")
            if not args.check:
                folder.mkdir(exist_ok=True)
                path.write_bytes(content)

    known = {SLUG_PREFIX + i["id"] for i in instances}
    orphans = sorted(p.name for p in ROOT.glob(SLUG_PREFIX + "*") if p.is_dir() and p.name not in known)
    if orphans:
        if args.prune and not args.check:
            for name in orphans:
                shutil.rmtree(ROOT / name)
            print("Silinen klasörler: " + ", ".join(orphans))
        else:
            print("UYARI: instances.yaml'da olmayan klasörler (silmek için --prune): " + ", ".join(orphans))
            if args.prune:
                changed.extend(orphans)

    print(f"Upstream sürüm: {new_version}")
    if old_versions and old_versions != {new_version}:
        print(f"Sürüm değişimi: {', '.join(sorted(old_versions))} -> {new_version}")
    print(f"Instance sayısı: {len(instances)}")

    if not changed:
        print("Değişiklik yok.")
        return 0
    verb = "Değişecek" if args.check else "Güncellenen"
    print(f"{verb} dosya sayısı: {len(changed)}")
    for c in changed:
        print("  " + c)
    return 1 if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
