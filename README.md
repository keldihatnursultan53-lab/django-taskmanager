# Task Manager (Django)

## Іске қосу
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

## Маршруттар
- GET /health/ → {"status": "ok"}
- ## Практикалық жұмыс 2: URL, View, HTTP

Маршруттар:
- GET / → басты бет
- GET /about/ → жоба туралы
- GET /tasks/ → тапсырмалар тізімі
- GET /tasks/<id>/ → бір тапсырма (табылмаса 404)
- POST /echo/ → жіберілген JSON-ды қайтарады (қате JSON → 400)

POST тексеру (Windows PowerShell):
```powershell
Set-Content -Path "$env:TEMP\good.json" -Value '{"name": "Aibek", "age": 19}'
curl.exe -i -X POST http://127.0.0.1:8000/echo/ -H "Content-Type: application/json" --data "@$env:TEMP\good.json"
```
## Практикалық жұмыс 3: Модельдер және SQLite

Модель Task: title, description, status (todo / in_progress / done), created_at.

Командалар:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py shell
```

ORM мысалдары:
```python
Task.objects.create(title="...", status="todo")
Task.objects.filter(status="done")
Task.objects.order_by("created_at")
```
## Практикалық жұмыс 4: Django Admin

Командалар:
```bash
python manage.py createsuperuser
python manage.py runserver
```

Админ панель: http://127.0.0.1:8000/admin/

Task моделінде бағандар: title, status, created_at. Сүзгі: status. Іздеу: title.