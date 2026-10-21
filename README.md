# Mitaş Zigbee2MQTT Add-ons

Mitaş fabrikasındaki her Sonoff Dongle Max için ayrı bir Zigbee2MQTT add-on'u içeren
Home Assistant add-on reposu. Klasörler elle yazılmaz, `tools/sync_z2m.py` tarafından
resmi repodan ([zigbee2mqtt/hassio-zigbee2mqtt](https://github.com/zigbee2mqtt/hassio-zigbee2mqtt))
üretilir.

HA'ya eklenecek URL: `https://github.com/homtreltd/mitas-zigbee2mqtt-addons`

## Nasıl çalışır

- Her `z2m_<id>/config.json`, resmi `config.json` dosyasının kopyasıdır. `instances.yaml`
  değerlerine göre şunlar farklıdır: `slug`, `name`, `url`, `description` (sonuna dongle IP'si
  eklenir), `options.data_path`, `options.mqtt.base_topic`, `options.serial` (`dongle_ip`
  doluysa), `options.watchdog` ve `8485/tcp` host portu.
- `version` ve `image` resmi repoyla birebir aynıdır. HA, Update'e basıldığında
  `ghcr.io/zigbee2mqtt/zigbee2mqtt-{arch}:<version>` imajını indirir. Repoda kod derlenmez.
- Farklı `slug` değerleri sayesinde HA her klasörü ayrı add-on olarak görür.
- `instances.yaml` varsayılanları (serial, base_topic, watchdog) **yalnızca add-on'un ilk
  kurulumunda** gelir. Kurulu bir add-on'un ayarını repo değişikliği değiştirmez: örneğin
  bir dongle'ın IP'si değişirse ilgili add-on'un Configuration sayfasındaki `serial.port`
  elle düzeltilir. Add-on Configuration değerleri, data klasöründeki `configuration.yaml`'ın
  önüne geçer; ikisini de aynı değere getir.
- MQTT sunucu, kullanıcı ve şifresi repoya yazılmaz (repo public). Boş kalınca add-on bunları
  Home Assistant'ın Mosquitto servisinden otomatik alır.

## Instance listesi

17 dongle `192.168.146.4` – `.20` aralığında. Kaynak: `instances.yaml` (tek doğruluk kaynağı).

| Dongle | id (slug = `z2m_<id>`) | Yer | IP | socat portu | data_path |
|---|---|---|---|---|---|
| 1 | `idari_bina_kat2_1` | İdari Bina Kat 2 | 192.168.146.5 | 8490 | `/config/idarikat-2dongle1` |
| 2 | `idari_bina_kat2_2` | İdari Bina Kat 2 | 192.168.146.4 | 8489 | `/config/idarikat-2dongle2` |
| 3 | `idari_bina_kat1_1` | İdari Bina Kat 1 | 192.168.146.7 | 8485 | `/config/binakat1` |
| 4 | `idari_bina_kat1_2` | İdari Bina Kat 1 | 192.168.146.6 | 8486 | `/config/binakat1iki` |
| 5 | `idari_bina_kat0_yemekhane_giris` | İdari Bina Zemin Kat Yemekhane Giriş | 192.168.146.8 | 8487 | `/config/zeminkatyemekhane` |
| 6 | `kaynak_depo_kapi_ustu` | Kaynak Depo Kapı Üstü | 192.168.146.9 | 8488 | `/config/kaynakdepo` |
| 7 | `idari_bina_kat0_kantin` | Zemin Kat Kantin | 192.168.146.10 | 8491 | `/config/z2m-zeminkat-kantin-dongle7` |
| 8 | `ndt_alani` | NDT Alanı | 192.168.146.11 | 8492 | `/config/z2m-ndt-alani` |
| 9 | `tup_alani` | Tüp Alanı | 192.168.146.18 | 8493 | `/config/z2m-tup-alani` |
| 10 | `mal_kabul` | Mal Kabul | 192.168.146.20 | 8494 | `/config/z2m-mal-kabul` |
| 11 | `beyaz_yaka_park_alani` | Beyaz Park Alanı | 192.168.146.15 | 8495 | `/config/z2m-beyaz-yaka-park-alani` |
| 12 | `revir` | Revir | 192.168.146.16 | 8496 | `/config/z2m-revir` |
| 13 | `imalat_hol_5` | İmalat Hol 5 | 192.168.146.12 | 8497 | `/config/z2m-imalat-hol-5` |
| 14 | `imalat_hol_4` | İmalat Hol 4 | 192.168.146.14 | 8498 | `/config/z2m-imalat-hol-4` |
| 15 | `imalat_hol_3` | İmalat Hol 3 | 192.168.146.13 | 8499 | `/config/z2m-imalat-hol-3` |
| 16 | `imalat_hol_2` | İmalat Hol 2 | 192.168.146.17 | 8500 | `/config/z2m-imalat-hol-2` |
| 17 | `imalat_hol_1` | İmalat Hol 1 | 192.168.146.19 | 8501 | `/config/z2m-imalat-hol-1` |

MQTT `base_topic` değeri `data_path` klasör adıdır. İstisna: Dongle 3 `zigbee2mqtt1`,
Dongle 4 `zigbee2mqtt2` (eski kurulumdaki topic'ler).

Aynı dongle'a veya aynı `data_path`'e iki add-on **aynı anda bağlanmamalı**. Bir add-on
taşınırken eskisi önce durdurulur.

## Watchdog

`sync_z2m.py` içindeki `WATCHDOG_DELAYS` (`0.5,2,3,5,3,1,1,1,1,3,3,3,3,3,3,3`, toplam 38,5 dk)
her `config.json`'a `options.watchdog` olarak yazılır. Z2M başarıyla başladıktan sonra
beklenmedik durursa (ör. `Adapter disconnected`) bu beklemelerle aynı process içinde yeniden
dener. İlk açılıştaki başlatma hatalarını kapsamaz; bunun için add-on'un Info sekmesinde
**Watchdog** (Supervisor) açık olmalı. **Auto update** kapalı kalır: CHANGELOG okunmadan
toplu güncelleme yapılmaz.

## Güncelleme (upstream yeni sürüm çıkardığında)

1. GitHub > Actions > **Sync Z2M** > Run workflow. Her pazartesi otomatik de çalışır.
   Elle yapmak için: `python tools/sync_z2m.py`, ardından commit ve push.
2. HA > Apps > ⋮ > Check for updates.
3. Önce tek bir instance'ı güncelle ve kontrol et, sonra diğerlerini güncelle.

## Yeni instance ekleme

1. `instances.yaml` dosyasına yeni bir satır ekle. `id`, `data_path`, `socat_port` ve
   `dongle_ip` değerleri benzersiz olmalı (`sync_z2m.py` tekrarı reddeder).
2. `python tools/sync_z2m.py`, ardından commit ve push.
3. HA > Apps > ⋮ > Check for updates. Yeni add-on listede görünür.
4. Add-on'u kur. Configuration'da `data_path`, `serial.port` ve `mqtt.base_topic` hazır gelir,
   kontrol edip Save > Start. Log'da adapter bağlantısı ve (varsa) `WATCHDOG` ayarı görülür.

**Dikkat:** Kurulu bir instance'ın `id` değerini değiştirme. HA onu yeni bir add-on olarak görür.

## Komutlar

```
python tools/sync_z2m.py            # üret / güncelle
python tools/sync_z2m.py --check    # sadece kontrol (değişiklik varsa exit 1)
python tools/sync_z2m.py --prune    # listeden çıkarılan z2m_* klasörlerini sil
```

Ayrıntılı doküman: Mitaş HA config reposu, `Mitas_HA_Automations/docs/zigbee2mqtt_coklu_instance.md`.
