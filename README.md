# Rustik Fox - Creator Embed Message

<p align="center">
  <img src="Assets/Git/wallpaper.png" alt="Rustic Fox Banner" width="100%">
</p>

[![СЕРВЕР ПОДДЕРЖКИ](https://img.shields.io/badge/СЕРВЕР_ПОДДЕРЖКИ-LOLKA.APP-cf1575?style=for-the-badge)](https://lolka.gg/gc7aPDzzK)

## Установка

### Создайте бота

Перейдите на [портал разработчиков](https://lolka.app/developers/portal) в Lolka.app и создайте там бота.

### Windows

1. Скачайте архив из [releases](https://github.com/vlad-boykov/creator_embed_message/releases)
1. Распакуйте архив в удобную папку.
2. Запустите `install.bat`.
3. После установки запустите `run.bat`.

Или вручную:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt
python main.py
```

Требуется Python 3.8+.

## Обновление v0.1.1

- Исправлен критический краш палитры цветов: `QLinearGradient` теперь получает `QPointF`.
- Кнопки сворачивания/разворачивания Embed и удаления Embed перерисованы как аккуратные векторные иконки без проблемных шрифтовых символов.
- Ссылка на портал разработчиков встроена непосредственно в пояснение к токену.
- Текстовые элементы настроек принудительно очищены от рамок.
