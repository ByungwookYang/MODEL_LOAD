# Multi-Model API with Docker

Docker를 통해 다양한 AI 모델(임베딩/리랭커/LLM)을 API화하여 서빙하는 프로젝트입니다.

## 🚀 주요 특징

- **지능형 모델 로더**: SentenceTransformer와 Transformers 자동 감지 및 로드
- **다양한 모델 타입 지원**: 임베딩, 리랭커, LLM 모델
- **완전 유연한 모델 교체**: .env 파일만 수정하면 즉시 다른 모델로 전환
- **Docker 기반**: 환경에 관계없이 일관된 실행
- **REST API**: 간단한 HTTP 요청으로 모델 사용
- **폐쇄망 지원**: 캐시된 모델을 활용한 오프라인 환경 지원

## 📁 프로젝트 구조

```
MODEL_LOAD/
├── .env.example          # 환경변수 예시 파일
├── .gitignore           # Git 무시 파일 목록
├── Dockerfile           # Docker 이미지 빌드 설정
├── docker-compose.yml   # Docker 서비스 설정
├── requirements.txt     # Python 패키지 목록
├── app.py              # 메인 API 서버 코드 (지능형 모델 로더 포함)
└── README.md           # 이 파일
```

## 🛠️ 설치 및 실행

### 1단계: AWS 서버 접속 및 모델 다운로드 폴더 이동

```bash
# Hugging Face 캐시 폴더로 이동
cd ~/.cache/huggingface/hub
```

### 2단계: 모델 다운로드

**Hugging Face CLI를 사용하여 .cache/huggingface/hub 위치에 모델 다운로드**

```bash
# Hugging Face CLI 설치 (없는 경우)
pip install huggingface_hub

# 임베딩 모델 다운로드
huggingface-cli download jinaai/jina-embeddings-v2-base-code
```

### 3단계: 모델 다운로드 확인

```bash
ls
```

**예상 결과:**
```bash
(base) ubuntu@ip-10-21-3-181:~/.cache/huggingface/hub$ ls
models--jinaai--jina-embeddings-v2-base-code
```

### 4단계: 도커라이징 파일 클론 준비

```bash
# 홈 디렉토리로 이동
cd ~

# 작업 폴더 생성
cd data

mkdir bw  # 임의 자기 자신 폴더 만들기

cd bw 
```

### 5단계: GitHub 저장소 클론

```bash
git clone https://github.com/ByungwookYang/MODEL_LOAD.git # 그대로 가져다가 필요한 부분만 수정하기 

cd MODEL_LOAD
```

### 6단계: 프로젝트 파일 확인

```bash
ls -la
```

**예상 결과:**
```bash
drwxrwxr-x  3 ubuntu ubuntu   4096 Aug 19 12:00 .
drwxrwxr-x  3 ubuntu ubuntu   4096 Aug 19 12:00 ..
-rw-rw-r--  1 ubuntu ubuntu    123 Aug 19 12:00 .env.example
-rw-rw-r--  1 ubuntu ubuntu    456 Aug 19 12:00 .gitignore
-rw-rw-r--  1 ubuntu ubuntu    789 Aug 19 12:00 Dockerfile
-rw-rw-r--  1 ubuntu ubuntu   1234 Aug 19 12:00 app.py
-rw-rw-r--  1 ubuntu ubuntu    567 Aug 19 12:00 docker-compose.yml
-rw-rw-r--  1 ubuntu ubuntu    890 Aug 19 12:00 requirements.txt
-rw-rw-r--  1 ubuntu ubuntu   2345 Aug 19 12:00 README.md
```

### 7단계: .env 파일 복사하기

cp .env.example .env

### 8단계: 필요 파일 수정

1) 
