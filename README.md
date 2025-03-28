# Paper Manager

```bash
python manage.py startapp paper
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8080
```

## Google Gemini Example

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={{KEY}}" ^
     -H "Content-Type: application/json" ^
     -d "{\"contents\": [{\"parts\": [{\"text\": \"안녕하세요, Gemini!\"}]}]}"
```
