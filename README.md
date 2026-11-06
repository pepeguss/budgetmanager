# Тихий счёт

Личный менеджер бюджета на Django и SQLite. Регистрации через сайт нет; учётная запись создаётся администратором. Все суммы отображаются в рублях.

## Первый запуск в Windows

В PowerShell из папки проекта:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py createsuperuser
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Откройте http://127.0.0.1:8000/ и войдите с созданным логином и паролем. Если виртуального окружения нет, создайте его командой `py -m venv venv` (требуется Python 3.12 или новее).

## Публикация через Cloudflare Tunnel

Подключите настроенный Cloudflare Tunnel к локальному адресу `http://127.0.0.1:8000` и своему домену. Перед запуском задайте переменные окружения в PowerShell, подставив свой домен и длинный случайный секретный ключ:

```powershell
$env:DJANGO_DEBUG = '0'
$env:DJANGO_SECRET_KEY = 'ЗАМЕНИТЕ-НА-ДЛИННЫЙ-СЛУЧАЙНЫЙ-СЕКРЕТНЫЙ-КЛЮЧ'
$env:DJANGO_ALLOWED_HOSTS = 'budget.example.com'
$env:DJANGO_CSRF_TRUSTED_ORIGINS = 'https://budget.example.com'
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py collectstatic --noinput
.\venv\Scripts\python.exe -m waitress --listen=127.0.0.1:8000 config.wsgi:application
```

Создать случайный ключ можно командой `.\venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`. Храните его в секрете и используйте один и тот же ключ при следующих запусках. Переменные PowerShell действуют только в текущем окне; настройте их постоянно для службы при постоянном размещении. Приложение должно получать HTTPS-запросы только через доверенный туннель: настройка доверяет заголовку `X-Forwarded-Proto`. Для дополнительной защиты рекомендуется ограничить доступ к домену через Cloudflare Access. Не открывайте порт приложения в интернет напрямую.

## Автопополнения и данные

Автопополнение создаётся каждый месяц в день первой даты; в коротком месяце — в последний день. При добавлении графика прошлые начисления создаются начиная с указанной даты. Начисления проверяются при входе на обзор, операции и страницу автопополнений, поэтому после простоя пропущенные начисления будут добавлены при следующем посещении. Для независимого запуска настройте планировщик Windows на ежедневное выполнение `C:\dev\budget\venv\Scripts\python.exe C:\dev\budget\manage.py process_recurring`. При повторном запуске дубликаты не создаются. После паузы при возобновлении графика пропущенные месяцы также будут начислены. Удалённое автоматическое начисление повторно не создаётся.

Файл `db.sqlite3` содержит все данные. Регулярно делайте его резервную копию при остановленном приложении и храните копии в защищённом месте.

## Проверка

```powershell
.\venv\Scripts\python.exe manage.py test
.\venv\Scripts\python.exe manage.py check
```
