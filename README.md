# 논문 관리 도구 (Paper Manager)

## 사용 방법

### 파이썬 설치

- <https://www.python.org/>에서 파이썬을 설치한다.

### 패키지 설치

- 아래의 명령으로 필요한 패키지를 설치한다.

```bash
pip install -r requirements.txt
```

### 서버 실행

- 아래의 명령으로 서버를 실행한다.

```bash
python manage.py runserver 8080
```

### 관리자 계정 생성

- 아래의 명령으로 관리자 계정을 생성한다.

```bash
python manage.py createsuperuser
```

### 서버 접속

- 웹 브라우저에서 <http://127.0.0.1:8080/>에 접속한다.

### 로그인

- 웹 브라우저에서 <http://127.0.0.1:8080/>에 접속한다.

### 논문 자동 요약을 위한 URL 및 API 설정

- **Google Gemini의 API 키**:
  - `.env` 파일에 Google Gemini의 API 키를 입력한다.
  - Google Gemini의 API 키는 <https://aistudio.google.com/apikey>에서 무료로 얻을 수 있다.
  - API 키 생성 후 API 제한사항에 "Generative Language API" 기능이 허용되어 있는지 확인한다.
- **OpenRouter의 API 키**:
  - `.env` 파일에 OpenRouter의 API 키를 입력한다.
  - OpenRouter의 API 키는 <https://openrouter.ai/settings/keys>에서 무료로 얻을 수 있다.
- **Ollama의 URL**:
  - `.env` 파일에 Ollama의 URL을 입력한다.
  - Ollama의 URL은 "http://{ip-address}:11434/api/generate"의 형식이다.

```text
GEMINI_API_KEY=<api_key_here>
OPENROUTER_API_KEY=<api_key_here>
OLLAMA_REQUEST_URL=http://127.0.0.1:11434/api/generate
```

### 자세한 사용 방법

- 자세한 사용 방법은 홈 화면을 참조한다.

![홈페이지](./static/images/home_manual.png)

## 개발자를 위한 노트

### 코드 다운로드

```bash
git clone git@github.com:doosik71/paperman2.git
```

### 데이터베이스 파일 생성

```bash
python manage.py makemigrations
python manage.py migrate
```

### 로컬 서버 실행

```bash
python manage.py runserver 8080
```
