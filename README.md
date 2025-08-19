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

### 1. 저장소 클론
```bash
git clone https://github.com/ByungwookYang/MODEL_LOAD.git
cd MODEL_LOAD
```

### 2. 환경변수 설정
```bash
# .env 파일 생성 (예시에서 복사하거나 직접 생성)
cp .env.example .env
# 또는
nano .env
```

**기본 .env 파일 내용:**
```bash
MODEL_PATH=/app/model
MODEL_NAME=jinaai/jina-embeddings-v2-base-code
MODEL_TYPE=embedding
PORT=8093
HOST=0.0.0.0
```

### 3. 모델 다운로드 (선택사항)
```bash
# Hugging Face CLI 설치
pip install huggingface_hub

# 모델 다운로드 (예시)
huggingface-cli download jinaai/jina-embeddings-v2-base-code
huggingface-cli download BAAI/bge-reranker-base
```

### 4. Docker 실행
```bash
# 백그라운드 실행
docker-compose up -d

# 실시간 로그 확인
docker-compose up
```

### 5. 서버 상태 확인
```bash
curl http://localhost:8093/health
```

## 🧠 지능형 모델 로더 시스템

이 프로젝트의 핵심 기능인 **4단계 자동 모델 로딩**:

1. **로컬 경로 + SentenceTransformer** 시도
2. **로컬 경로 + Transformers AutoModel** 시도  
3. **모델명 + SentenceTransformer** 시도
4. **모델명 + Transformers AutoModel** 시도

어떤 모델이든 자동으로 적합한 방식을 찾아서 로드합니다!

## 🔧 모델 타입별 설정

### Embedding 모델 (임베딩)
```bash
MODEL_TYPE=embedding
MODEL_NAME=jinaai/jina-embeddings-v2-base-code
```
- **지원 엔드포인트**: `/embedding`
- **용도**: 텍스트를 벡터로 변환
- **추천 모델**: 
  - `jinaai/jina-embeddings-v2-base-code` (코드 특화)
  - `sentence-transformers/all-MiniLM-L6-v2` (다목적)
  - `intfloat/multilingual-e5-large` (다국어)

### Reranker 모델 (순위 재정렬)
```bash
MODEL_TYPE=reranker
MODEL_NAME=BAAI/bge-reranker-base
```
- **지원 엔드포인트**: `/reranker`
- **용도**: 검색 결과 순위 재정렬
- **추천 모델**: 
  - `BAAI/bge-reranker-base`
  - `cross-encoder/ms-marco-MiniLM-L-12-v2`

### LLM 모델 (텍스트 생성)
```bash
MODEL_TYPE=llm
MODEL_NAME=microsoft/DialoGPT-medium
```
- **지원 엔드포인트**: `/v1`
- **용도**: 텍스트 생성 및 대화
- **추천 모델**: 
  - `microsoft/DialoGPT-medium`
  - `gpt2`

## 📡 API 사용법

### 서버 상태 확인
```bash
GET http://localhost:8093/health
```

**응답:**
```json
{
  "status": "ok",
  "model_type": "embedding",
  "loaded_with": "sentence_transformer",
  "model_loaded": true,
  "supported_endpoints": ["/embedding"]
}
```

### Embedding API
```bash
curl -X POST http://localhost:8093/embedding \
  -H "Content-Type: application/json" \
  -d '{"texts": ["안녕하세요", "Hello world"]}'
```

**응답:**
```json
{
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "shape": [2, 768],
  "model_type": "sentence_transformer"
}
```

### Reranker API
```bash
curl -X POST http://localhost:8093/reranker \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python programming",
    "documents": ["Learn Python basics", "JavaScript tutorial", "Python advanced concepts"]
  }'
```

**응답:**
```json
{
  "scores": [0.9, 0.2, 0.8],
  "query": "python programming",
  "documents": ["Learn Python basics", "JavaScript tutorial", "Python advanced concepts"]
}
```

### LLM API
```bash
curl -X POST http://localhost:8093/v1 \
  -H "Content-Type: application/json" \
  -d '{"prompt": "안녕하세요"}'
```

**응답:**
```json
{
  "prompt": "안녕하세요",
  "response": "안녕하세요! 무엇을 도와드릴까요?"
}
```

## 🔄 모델 교체하기 (초간단!)

### 1. 다른 임베딩 모델로 변경
```bash
# .env 파일 수정
MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
MODEL_TYPE=embedding
```

### 2. 리랭커 모델로 변경
```bash
# .env 파일 수정
MODEL_NAME=BAAI/bge-reranker-base
MODEL_TYPE=reranker
```

### 3. 즉시 적용
```bash
docker-compose down && docker-compose up -d
```

**재빌드 필요 없음!** 환경변수만 바꾸면 끝!

## 🌐 폐쇄망 환경 지원

### 모델 미리 다운로드
```bash
# 인터넷 연결된 환경에서
huggingface-cli download jinaai/jina-embeddings-v2-base-code --local-dir ./models/jina-embeddings

# 폐쇄망으로 모델 폴더 복사 후
MODEL_PATH=./models/jina-embeddings
```

### docker-compose.yml 볼륨 설정
```yaml
volumes:
  - ./models:/app/models
  - ~/.cache/huggingface:/root/.cache/huggingface
```

## 🐛 문제 해결

### 모델 로드 실패
```bash
# 로그 확인
docker-compose logs

# 지원되는 모델인지 확인
curl http://localhost:8093/health
```

### 포트 충돌
```bash
# .env 파일에서 포트 변경
PORT=8094
```

### 메모리 부족
- Docker Desktop에서 메모리 할당량 증가 (8GB 이상 권장)
- 더 작은 모델 사용: `sentence-transformers/all-MiniLM-L6-v2`

### Docker 캐시 문제
```bash
# 강제 재빌드
docker-compose build --no-cache
docker-compose up
```

## 💡 활용 예시

### 의미 검색 시스템
1. 문서들을 임베딩으로 변환
2. 검색 쿼리도 임베딩으로 변환
3. 코사인 유사도로 관련 문서 찾기
4. 리랭커로 정확도 향상

### RAG (Retrieval-Augmented Generation)
1. 임베딩으로 관련 문서 검색
2. 리랭커로 최적 문서 선별
3. LLM으로 답변 생성
