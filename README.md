
# 🏠 Devices Monitor v1.0.7 (Full)

Интеграция Home Assistant для мониторинга выключателей и сенсоров.

## 🚀 Возможности
- Контроль выключателей и сенсоров
- Раздельные уведомления и расписания
- Пороговые правила (above/below) для сенсоров
- Поддержка TTS (озвучка)
- Blueprints для автоматизаций
- Сервисы теста и отчётов

## ⚙️ Установка
1. Скопируйте папку `custom_components/devices_monitor` в `/config/custom_components/`
2. Перезапустите Home Assistant
3. Добавьте интеграцию через **Настройки → Устройства и службы → Добавить интеграцию → Devices Monitor**

## 🧪 Сервисы
- `devices_monitor.test_switches_notify`
- `devices_monitor.test_sensors_notify`
- `devices_monitor.send_report`

## 📑 Blueprints
После установки доступны шаблоны автоматизаций: отчёты и тесты.
