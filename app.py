from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import logging

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 환경변수에서 설정 읽기
MODEL_PATH = os.getenv('MODEL_PATH', '/app/model')
MODEL_TYPE = os.getenv('MODEL_TYPE', 'embedding').lower()
PORT = int(os.getenv('PORT', 8093))
HOST = os.getenv('HOST', '0.0.0.0')

# 모델 로드
model = None
supported_endpoints = []

def load_model():
    global model, supported_endpoints
    try:
        logger.info(f"모델 타입: {MODEL_TYPE}, 경로: {MODEL_PATH}")
        
        if MODEL_TYPE == 'embedding':
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(MODEL_PATH)
            supported_endpoints = ['/embedding']
        
        elif MODEL_TYPE == 'reranker':
            from sentence_transformers import CrossEncoder
            model = CrossEncoder(MODEL_PATH)
            supported_endpoints = ['/reranker']
        
        elif MODEL_TYPE == 'llm':
            from transformers import AutoTokenizer, AutoModelForCausalLM
            model = {
                'tokenizer': AutoTokenizer.from_pretrained(MODEL_PATH),
                'model': AutoModelForCausalLM.from_pretrained(MODEL_PATH)
            }
            supported_endpoints = ['/v1']
        
        else:
            raise ValueError(f"지원하지 않는 모델 타입: {MODEL_TYPE}")
            
        logger.info(f"모델 로드 완료! 지원 엔드포인트: {supported_endpoints}")
        
    except Exception as e:
        logger.error(f"모델 로드 실패: {e}")

def check_endpoint_support(endpoint):
    """엔드포인트 지원 여부 확인"""
    if endpoint not in supported_endpoints:
        return jsonify({
            "error": f"이 모델({MODEL_TYPE})은 {endpoint} 엔드포인트를 지원하지 않습니다",
            "supported_endpoints": supported_endpoints
        }), 404
    return None

# 임베딩 엔드포인트
@app.route('/embedding', methods=['POST'])
def embedding():
    error_response = check_endpoint_support('/embedding')
    if error_response:
        return error_response
    
    try:
        data = request.json
        texts = data.get('texts', [])
        if not isinstance(texts, list):
            texts = [texts]
        
        embeddings = model.encode(texts)
        return jsonify({
            "embeddings": embeddings.tolist(),
            "shape": list(embeddings.shape)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 리랭커 엔드포인트
@app.route('/reranker', methods=['POST'])
def reranker():
    error_response = check_endpoint_support('/reranker')
    if error_response:
        return error_response
    
    try:
        data = request.json
        query = data.get('query', '')
        documents = data.get('documents', [])
        
        pairs = [[query, doc] for doc in documents]
        scores = model.predict(pairs)
        
        return jsonify({
            "scores": scores.tolist(),
            "query": query,
            "documents": documents
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# LLM 생성 엔드포인트 (기본 생성만)
@app.route('/v1', methods=['POST'])
def v1_generate():
    error_response = check_endpoint_support('/v1')
    if error_response:
        return error_response
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        inputs = model['tokenizer'](prompt, return_tensors="pt")
        outputs = model['model'].generate(inputs['input_ids'])
        
        response = model['tokenizer'].decode(outputs[0], skip_special_tokens=True)
        
        return jsonify({
            "prompt": prompt,
            "response": response
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "model_type": MODEL_TYPE,
        "model_loaded": model is not None,
        "supported_endpoints": supported_endpoints
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": f"Multi-Model API ({MODEL_TYPE})",
        "supported_endpoints": supported_endpoints,
        "health": "/health"
    })

if __name__ == '__main__':
    load_model()
    logger.info(f"서버 시작: {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False)