
# 🏠 Devices Monitor v1.0.6

Интеграция Home Assistant для мониторинга выключателей и датчиков.

## 🚀 Возможности
- Раздельные уведомления для выключателей и сенсоров (текст и TTS)
- Раздельные расписания отчётов
- Пороговые правила по каждому сенсору (above/below + message)
- Полный выбор сервисов уведомлений в UI

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
