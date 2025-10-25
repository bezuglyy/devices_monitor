
# 🏠 Devices Monitor v1.0.4

Полностью рабочая интеграция Home Assistant для мониторинга **выключателей/света** и **датчиков** в одной интеграции.
- Раздельные расписания отчётов для выключателей и датчиков
- Раздельные каналы уведомлений (выключатели — только текст; датчики — текст + TTS)
- Пороговые правила для `sensor` (`above`/`below` + `message`)
- Сервисы: `send_report (target)`, `test_switches_notify`, `test_sensors_notify`

## ⚙️ Настройка через UI
1) Добавьте интеграцию **Devices Monitor** → укажите:
- режим (`switches` / `sensors` / `both`)
- интервал (мин) для регулярного отчёта
- расписание отчётов для выключателей/датчиков (каждый на своей строке, формат `HH:MM`)

2) Откройте **Параметры** интеграции и укажите:
- `switches_list` — список `switch`/`light`
- `switches_notify_on/off/report` — сервисы notify для выключателей
- `sensors_binary` — список `binary_sensor`
- `sensors_thresholds` — правила для `sensor`, пример ниже
- `sensors_notify_on/off` — сервисы notify для переходов ON/OFF по бинарным сенсорам
- `sensors_notify_alerts` — список сервисов notify (по одному на строку) для пороговых событий и отчётов
- `sensors_notify_tts` — список `media_player` (по одному на строке) для озвучки

## 📄 Пример правил порогов
```
sensor.temperature_bedroom; above=28; message=🔥 Жарко в спальне: {value}°C
sensor.humidity_bathroom; above=80; message=💧 Влажность в ванной: {value}%
sensor.co2_office; above=1000; message=⚠️ CO₂ высокий: {value} ppm
sensor.temperature_kids; below=18; message=❄️ Холодно в детской: {value}°C
```

## 🧪 Примеры сервисов
```yaml
service: devices_monitor.test_switches_notify
data:
  title: "Тест выключателей"
  message: "Это тест уведомлений выключателей"
```

```yaml
service: devices_monitor.test_sensors_notify
data:
  title: "Тест сенсоров"
  message: "Это тест уведомлений сенсоров"
```

```yaml
service: devices_monitor.send_report
data:
  target: sensors   # switches | sensors | both
```

## 📦 Структура
- `custom_components/devices_monitor/` — код интеграции
- `hacs.json`, `LICENSE`, `README.md` — метаданные для GitHub/HACS
