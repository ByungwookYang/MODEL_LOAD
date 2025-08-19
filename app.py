from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import logging
import torch

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 환경변수에서 설정 읽기
MODEL_PATH = os.getenv('MODEL_PATH', '/app/model')
MODEL_NAME = os.getenv('MODEL_NAME', 'jinaai/jina-embeddings-v2-base-code')
MODEL_TYPE = os.getenv('MODEL_TYPE', 'embedding').lower()
PORT = int(os.getenv('PORT', 8093))
HOST = os.getenv('HOST', '0.0.0.0')

# 모델 로드
model = None
supported_endpoints = []

def try_sentence_transformer_load(model_identifier):
    """SentenceTransformer로 모델 로드 시도"""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_identifier)
        logger.info(f"SentenceTransformer로 모델 로드 성공: {model_identifier}")
        return model, 'sentence_transformer'
    except Exception as e:
        logger.warning(f"SentenceTransformer 로드 실패: {e}")
        return None, None

def try_transformers_load(model_identifier):
    """Transformers AutoModel로 모델 로드 시도"""
    try:
        from transformers import AutoModel, AutoTokenizer
        
        # MODEL_NAME이 models-- 형태라면 변환
        if 'models--' in str(model_identifier):
            model_name = model_identifier.replace('models--', '').replace('--', '/')
        else:
            model_name = model_identifier
            
        model = {
            'model': AutoModel.from_pretrained(model_name),
            'tokenizer': AutoTokenizer.from_pretrained(model_name)
        }
        logger.info(f"Transformers AutoModel로 모델 로드 성공: {model_name}")
        return model, 'transformers'
    except Exception as e:
        logger.warning(f"Transformers AutoModel 로드 실패: {e}")
        return None, None

def load_model():
    global model, supported_endpoints
    try:
        logger.info(f"모델 타입: {MODEL_TYPE}, 경로: {MODEL_PATH}")
        
        if MODEL_TYPE == 'embedding':
            model_loaded = False
            model_type = None
            
            # 1순위: 로컬 경로로 SentenceTransformer 시도
            if os.path.exists(MODEL_PATH):
                logger.info(f"로컬 경로 시도: {MODEL_PATH}")
                model, model_type = try_sentence_transformer_load(MODEL_PATH)
                if model is not None:
                    model_loaded = True
            
            # 2순위: 로컬 경로로 Transformers 시도
            if not model_loaded and os.path.exists(MODEL_PATH):
                logger.info(f"로컬 경로로 Transformers 시도: {MODEL_PATH}")
                model, model_type = try_transformers_load(MODEL_PATH)
                if model is not None:
                    model_loaded = True
            
            # 3순위: MODEL_NAME으로 SentenceTransformer 시도
            if not model_loaded:
                logger.info(f"MODEL_NAME으로 SentenceTransformer 시도: {MODEL_NAME}")
                model_name = MODEL_NAME.replace('models--', '').replace('--', '/') if 'models--' in MODEL_NAME else MODEL_NAME
                model, model_type = try_sentence_transformer_load(model_name)
                if model is not None:
                    model_loaded = True
            
            # 4순위: MODEL_NAME으로 Transformers 시도
            if not model_loaded:
                logger.info(f"MODEL_NAME으로 Transformers 시도: {MODEL_NAME}")
                model, model_type = try_transformers_load(MODEL_NAME)
                if model is not None:
                    model_loaded = True
            
            if model_loaded:
                # 모델 타입에 따라 전역 변수 설정
                globals()['model_type'] = model_type
                supported_endpoints = ['/embedding']
                logger.info(f"임베딩 모델 로드 완료! 타입: {model_type}")
            else:
                raise Exception("모든 방법으로 임베딩 모델 로드 실패")
        
        elif MODEL_TYPE == 'reranker':
            from sentence_transformers import CrossEncoder
            model = CrossEncoder(MODEL_PATH)
            globals()['model_type'] = 'cross_encoder'
            supported_endpoints = ['/reranker']
        
        elif MODEL_TYPE == 'llm':
            from transformers import AutoTokenizer, AutoModelForCausalLM
            model = {
                'tokenizer': AutoTokenizer.from_pretrained(MODEL_PATH),
                'model': AutoModelForCausalLM.from_pretrained(MODEL_PATH)
            }
            globals()['model_type'] = 'llm'
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
        
        # 모델 타입에 따라 다르게 처리
        if globals().get('model_type') == 'sentence_transformer':
            # SentenceTransformer 방식
            embeddings = model.encode(texts)
            return jsonify({
                "embeddings": embeddings.tolist(),
                "shape": list(embeddings.shape),
                "model_type": "sentence_transformer"
            })
        
        elif globals().get('model_type') == 'transformers':
            # Transformers 방식
            inputs = model['tokenizer'](texts, padding=True, truncation=True, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model['model'](**inputs)
            
            # 평균 풀링으로 문장 임베딩 생성
            embeddings = outputs.last_hidden_state.mean(dim=1)
            
            return jsonify({
                "embeddings": embeddings.numpy().tolist(),
                "shape": list(embeddings.shape),
                "model_type": "transformers"
            })
        
        else:
            return jsonify({"error": "지원되지 않는 모델 타입"}), 500
            
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
        "loaded_with": globals().get('model_type', 'unknown'),
        "model_loaded": model is not None,
        "supported_endpoints": supported_endpoints
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": f"Multi-Model API ({MODEL_TYPE})",
        "loaded_with": globals().get('model_type', 'unknown'),
        "supported_endpoints": supported_endpoints,
        "health": "/health"
    })

if __name__ == '__main__':
    load_model()
    logger.info(f"서버 시작: {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False)
