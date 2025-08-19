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

## 🛠️ 인터넷망에서 설치 및 실행확인

### 1단계: AWS 서버 접속 및 모델 다운로드 폴더 이동
#### Hugging Face 캐시 폴더로 이동
```bash
cd ~/.cache/huggingface/hub
```

### 2단계: 모델 다운로드

**Hugging Face CLI를 사용하여 .cache/huggingface/hub 위치에 모델 다운로드**
#### Hugging Face CLI 설치 (없는 경우)
```bash
pip install huggingface_hub
```

#### 임베딩 모델 다운로드
```bash
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
git clone https://github.com/ByungwookYang/MODEL_LOAD.git

cd MODEL_LOAD
```

### 6단계: 프로젝트 파일 확인

```bash
ls -la
```

**예상 결과:**
```bash
drwxrwxr-x 3 ubuntu ubuntu 4096 Aug 19 14:03 .
drwxrwxr-x 3 ubuntu ubuntu 4096 Aug 19 14:03 ..
-rw-rw-r-- 1 ubuntu ubuntu  175 Aug 19 14:03 .env.example
drwxrwxr-x 8 ubuntu ubuntu 4096 Aug 19 14:03 .git
-rw-rw-r-- 1 ubuntu ubuntu   74 Aug 19 14:03 .gitignore
-rw-rw-r-- 1 ubuntu ubuntu  150 Aug 19 14:03 Dockerfile
-rw-rw-r-- 1 ubuntu ubuntu 7208 Aug 19 14:03 README.md
-rw-rw-r-- 1 ubuntu ubuntu 9046 Aug 19 14:03 app.py
-rw-rw-r-- 1 ubuntu ubuntu  224 Aug 19 14:03 docker-compose.yml
-rw-rw-r-- 1 ubuntu ubuntu   48 Aug 19 14:03 requirements.txt
```

### 7단계: .env 파일 복사하기

```bash
cp .env.example .env

cat .env
```

**예상 결과:**
```bash
MODEL_PATH=/app/model
MODEL_NAME=jinaai/jina-embeddings-v2-base-code
MODEL_TYPE=embedding
PORT=8093
HOST=0.0.0.0
```

### 8단계: 필요 파일 수정 -> 여기만 개인 모델에 맞게 설정

**1) docker-compose.yml 수정**
```bash
nano docker-compose.yml
```

**포트 설정 수정 (환경변수 → 직접 값):**
```yaml
version: '3.8'
services:
  sentence-transformer-api: # 도커 이미지 이름 설정(변경가능)
    build: .
    ports:
      - "${PORT}:${PORT}"
    volumes:
      - ~/.cache/huggingface/hub/${MODEL_NAME}/snapshots/${SNAPSHOT_ID}:/app/model # 경로 지정 가능 (모델 폴터명, snapshot 해시값은 환경변수에서 받아옴)
    env_file:
      - .env
```

**2) .env 파일 확인 및 수정 (필요시)**
```bash
nano .env
```

```bash
MODEL_PATH=/app/model
MODEL_NAME=models--jinaai--jina-embeddings-v2-base-code # 모델 폴더명 입력(변경가능)
SNAPSHOT_ID=516f4baf13dec4ddddda8631e019b5737c8bc250 # 해시값 입력 -> snapshots 폴더 안 해시폴더명(변경가능)
MODEL_TYPE=embedding # 모델 타입명 (v1/embedding/rerank 중 선택가능)
PORT=8093 # 사용 가능 포트로 변경
HOST=0.0.0.0
```

### 9단계: Docker 빌드 및 실행

```bash
# 캐시 없이 완전 재빌드
docker-compose build --no-cache # 시간 조금 걸림

# 백그라운드에서 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

**예상 성공 로그:**
```bash
sentence-transformer-api_1  | INFO:__main__:모델 타입: embedding, 경로: /app/model
sentence-transformer-api_1  | INFO:__main__:MODEL_NAME으로 SentenceTransformer 시도: jinaai/jina-embeddings-v2-base-code
sentence-transformer-api_1  | INFO:__main__:SentenceTransformer로 모델 로드 성공: jinaai/jina-embeddings-v2-base-code
sentence-transformer-api_1  | INFO:__main__:임베딩 모델 로드 완료! 타입: sentence_transformer
sentence-transformer-api_1  | INFO:__main__:모델 로드 완료! 지원 엔드포인트: ['/embedding']
sentence-transformer-api_1  | INFO:__main__:서버 시작: 0.0.0.0:8093
```

### 10단계:상태 확인
#### 1) 서버 상태 확인
```bash
curl http://localhost:8093/health
```

**예상 응답:**
```json
{
  "status": "ok",
  "model_type": "embedding",
  "loaded_with": "sentence_transformer",
  "model_loaded": true,
  "supported_endpoints": ["/embedding"]  # 엔드포인트 확인
}
```

#### 2) API 테스트

```bash
# 임베딩 API 테스트
curl -X POST http://localhost:8093/embedding \ # 엔드포인트 변경해줘야함
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello world", "안녕하세요"]}'
```

**예상 응답:**
```json
{
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "shape": [2, 768],
  "model_type": "sentence_transformer"
}
```

#### 3) 도커 이미지 확인
```bash
docker images
```


**예상 결과:**
```bash
(base) ubuntu@ip-10-21-3-181:~/data/bw/MODEL_LOAD$ docker images
REPOSITORY                            TAG       IMAGE ID       CREATED             SIZE
model_load_sentence-transformer-api   latest    939135af1f59   8 minutes ago       11.3GB
```

### 11단계: 이미지를 tar로 저장

```bash
docker save model_load_sentence-transformer-api > model_load_api.tar

# 2. 2GB씩 분할
split -b 2G model_load_api.tar model_load_api.tar.part_

# 3. 원본 tar 삭제 (용량 절약)
rm model_load_api.tar

# 4. 분할된 파일들 확인
ls -lh model_load_api.tar.part_*
```

### 12단계: 메모리 정리


## 🔄 다른 모델로 변경하기

### Reranker 모델로 변경

```bash
# 1. 리랭커 모델 다운로드
huggingface-cli download BAAI/bge-reranker-base

# 2. .env 파일 수정
nano .env
```

**.env 파일 내용 변경:**
```bash
MODEL_NAME=BAAI/bge-reranker-base
MODEL_TYPE=reranker
```

```bash
# 3. 재시작
docker-compose down
docker-compose up -d
```

### LLM 모델로 변경

```bash
# 1. LLM 모델 다운로드
huggingface-cli download microsoft/DialoGPT-medium

# 2. .env 파일 수정
MODEL_NAME=microsoft/DialoGPT-medium
MODEL_TYPE=llm

# 3. 재시작
docker-compose down
docker-compose up -d
```

## 🐛 문제 해결

### 모델 로드 실패
```bash
# 로그 확인
docker-compose logs

# 모델 파일 확인
ls ~/.cache/huggingface/hub/models--jinaai--jina-embeddings-v2-base-code/
```

### 포트 충돌
```bash
# .env 파일에서 포트 변경
PORT=8094
```

### Docker 캐시 문제
```bash
# 강제 재빌드
docker-compose build --no-cache
docker-compose up
```

## 📋 요구사항

- **Docker & Docker Compose** (필수)
- **Python 3.9+** (Hugging Face CLI용)
- **최소 8GB RAM** (모델 크기에 따라)
- **인터넷 연결** (모델 다운로드용)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다.

---

**Made with ❤️ for AI Engineers**
