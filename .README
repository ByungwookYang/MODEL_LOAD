# Multi-Model API with Docker

Docker를 통해 다양한 AI 모델(임베딩/리랭커/LLM)을 API화하여 서빙하는 프로젝트입니다.

## 🚀 주요 특징

- **다양한 모델 타입 지원**: 임베딩, 리랭커, LLM 모델
- **유연한 모델 교체**: .env 파일만 수정하면 다른 모델로 전환 가능
- **Docker 기반**: 환경에 관계없이 일관된 실행
- **REST API**: 간단한 HTTP 요청으로 모델 사용

## 📁 프로젝트 구조

```
MODEL_LOAD/
├── .env.example          # 환경변수 예시 파일
├── .gitignore           # Git 무시 파일 목록
├── Dockerfile           # Docker 이미지 빌드 설정
├── docker-compose.yml   # Docker 서비스 설정
├── requirements.txt     # Python 패키지 목록
├── app.py              # 메인 API 서버 코드
└── README.md           # 이 파일
```

## 🛠️ 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/ByungwookYang/MODEL_LOAD.git
cd MODEL_LOAD
```

### 2. 환경변수 설정
```bash
cp .env.example .env
```

### 3. .env 파일 수정
본인 환경에 맞게 `.env` 파일을 수정하세요:

```bash
MODEL_PATH=/app/model
MODEL_NAME=models--sentence-transformers--all-MiniLM-L6-v2
SNAPSHOT_ID=c9745ed1d9f207416be6d2e6f8de32d1f16199bf
MODEL_TYPE=embedding
PORT=8093
HOST=0.0.0.0
```

**수정해야 할 부분:**
- `MODEL_NAME`: 사용할 모델 이름
- `SNAPSHOT_ID`: 실제 스냅샷 ID (아래 명령어로 확인)
- `MODEL_TYPE`: 모델 타입 (embedding/reranker/llm)
- `PORT`: 사용할 포트 번호

### 4. 실제 모델 경로 확인
```bash
# 모델 목록 확인
ls ~/sw/llm/.cache/huggingface/hub/

# 스냅샷 ID 확인
ls ~/sw/llm/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/
```

### 5. Docker 실행
```bash
docker-compose up --build
```

## 🔧 모델 타입별 설정

### Embedding 모델
```bash
MODEL_TYPE=embedding
```
- **지원 엔드포인트**: `/embedding`
- **용도**: 텍스트를 벡터로 변환

### Reranker 모델
```bash
MODEL_TYPE=reranker
```
- **지원 엔드포인트**: `/reranker`
- **용도**: 문서 순위 재정렬

### LLM 모델
```bash
MODEL_TYPE=llm
```
- **지원 엔드포인트**: `/v1`
- **용도**: 텍스트 생성

## 📡 API 사용법

### 서버 상태 확인
```bash
GET http://localhost:8093/health
```

### Embedding API
```bash
POST http://localhost:8093/embedding
Content-Type: application/json

{
  "texts": ["안녕하세요", "Hello world"]
}
```

**응답:**
```json
{
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "shape": [2, 384]
}
```

### Reranker API
```bash
POST http://localhost:8093/reranker
Content-Type: application/json

{
  "query": "검색 쿼리",
  "documents": ["문서1", "문서2", "문서3"]
}
```

**응답:**
```json
{
  "scores": [0.8, 0.6, 0.9],
  "query": "검색 쿼리",
  "documents": ["문서1", "문서2", "문서3"]
}
```

### LLM API
```bash
POST http://localhost:8093/v1
Content-Type: application/json

{
  "prompt": "안녕하세요"
}
```

**응답:**
```json
{
  "prompt": "안녕하세요",
  "response": "안녕하세요! 무엇을 도와드릴까요?"
}
```

## 🔄 다른 모델로 변경하기

### 1. 다른 임베딩 모델 사용
```bash
# .env 파일 수정
MODEL_NAME=models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2
SNAPSHOT_ID=새로운_스냅샷_ID
MODEL_TYPE=embedding
```

### 2. 리랭커 모델로 변경
```bash
# .env 파일 수정
MODEL_NAME=models--cross-encoder--ms-marco-MiniLM-L-12-v2
SNAPSHOT_ID=새로운_스냅샷_ID
MODEL_TYPE=reranker
```

### 3. Docker 재시작
```bash
docker-compose down
docker-compose up --build
```

## 🐛 문제 해결

### 모델 로드 실패
- 모델 경로가 올바른지 확인
- 스냅샷 ID가 정확한지 확인
- 모델 파일이 실제로 존재하는지 확인

### 포트 충돌
- `.env` 파일에서 다른 포트 번호로 변경
- `docker-compose.yml`에서도 포트 매핑 확인

### 메모리 부족
- Docker Desktop에서 메모리 할당량 증가
- 더 작은 모델 사용 고려

## 📋 요구사항

- Docker & Docker Compose
- Python 3.10+
- Hugging Face 모델 파일
- 충분한 메모리 (모델 크기에 따라)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다.

## 🙋‍♂️ 문의

문제가 있거나 개선사항이 있다면 Issues를 생성해주세요!
