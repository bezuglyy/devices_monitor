
# 🏠 Devices Monitor v1.0.5

Интеграция Home Assistant для мониторинга выключателей и датчиков.

## 🚀 Возможности
- Раздельные уведомления: выключатели → текст, сенсоры → текст + TTS
- Раздельные расписания отчётов для выключателей и датчиков
- Пороговые правила для сенсоров (каждый сенсор со своими `above`/`below`)
- Поддержка нескольких правил для одного сенсора
- Сервисы для теста и отчётов

## 📂 Пример настроек сенсоров
```yaml
sensors_thresholds:
  sensor.temperature_bedroom:
    above: 28
    message_above: "🔥 Жарко: {value}°C"
    below: 18
    message_below: "❄️ Холодно: {value}°C"
  sensor.co2_office:
    above: 1000
    message_above: "⚠️ CO₂ высокий: {value} ppm"
```

## 🧪 Сервисы
```yaml
service: devices_monitor.test_switches_notify
service: devices_monitor.test_sensors_notify
service: devices_monitor.send_report
data:
  target: sensors   # switches | sensors | both
```
