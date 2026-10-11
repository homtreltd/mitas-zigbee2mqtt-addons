# Mitaş Zigbee2MQTT Add-ons

Mitaş fabrikasındaki her Sonoff Dongle Max için ayrı bir Zigbee2MQTT add-on'u içeren
Home Assistant add-on reposu. Klasörler elle yazılmaz, `tools/sync_z2m.py` tarafından
resmi repodan ([zigbee2mqtt/hassio-zigbee2mqtt](https://github.com/zigbee2mqtt/hassio-zigbee2mqtt))
üretilir.

HA'ya eklenecek URL: `https://github.com/homtreltd/mitas-zigbee2mqtt-addons`

## Nasıl çalışır

- Her `z2m_<id>/config.json`, resmi `config.json` dosyasının kopyasıdır. Sadece `slug`,
  `name`, `url`, `description`, `options.data_path` ve `8485/tcp` host portu farklıdır.
- `version` ve `image` resmi repoyla birebir aynıdır. HA, Update'e basıldığında
  `ghcr.io/zigbee2mqtt/zigbee2mqtt-{arch}:<version>` imajını indirir. Repoda kod derlenmez.
- Farklı `slug` değerleri sayesinde HA her klasörü ayrı add-on olarak görür.

## Güncelleme (upstream yeni sürüm çıkardığında)

1. GitHub > Actions > **Sync Z2M** > Run workflow. Her pazartesi otomatik de çalışır.
   Elle yapmak için: `python tools/sync_z2m.py`, ardından commit ve push.
2. HA > Apps > ⋮ > Check for updates.
3. Önce tek bir instance'ı güncelle ve kontrol et, sonra diğerlerini güncelle.

## Yeni instance ekleme

1. `instances.yaml` dosyasına yeni bir satır ekle. `id`, `data_path` ve `socat_port`
   değerleri benzersiz olmalı.
2. `python tools/sync_z2m.py`, ardından commit ve push.
3. HA > Apps > ⋮ > Check for updates. Yeni add-on listede görünür.

**Dikkat:** Kurulu bir instance'ın `id` değerini değiştirme. HA onu yeni bir add-on olarak görür.

## Komutlar

```
python tools/sync_z2m.py            # üret / güncelle
python tools/sync_z2m.py --check    # sadece kontrol (değişiklik varsa exit 1)
python tools/sync_z2m.py --prune    # listeden çıkarılan z2m_* klasörlerini sil
```

Ayrıntılı doküman: Mitaş HA config reposu, `Mitas_HA_Automations/docs/zigbee2mqtt_coklu_instance.md`.
