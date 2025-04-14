# 학습 보조 서버 (Learning Assistant Server)

PDF 문서를 분석하여 핵심 개념을 마크다운으로 정리하는 서버입니다.

## 기능

- PDF 파일 업로드 및 텍스트 추출
- 핵심 개념 자동 추출 및 요약 (EXAONE 모델 사용)
- 마크다운 형식으로 정리된 문서 생성
- HTML 미리보기 제공
- Ollama 서버 자동 실행 및 관리

## 사전 요구사항

1. [Ollama 설치](https://ollama.ai/download)
2. EXAONE 모델 다운로드:
```bash
ollama pull exaone3.5:7.8b
```

## 설치 방법

1. 프로젝트 클론:
```bash
git clone [repository-url]
cd learning-assistant-server
```

2. 가상환경 생성 및 활성화:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. 의존성 설치:
```bash
pip install -e .
```

## 서버 실행

```bash
python main.py
```

서버가 `http://localhost:8000`에서 실행되며, Ollama 서버는 자동으로 시작됩니다.
서버를 종료하면 Ollama 서버도 자동으로 종료됩니다.

## API 사용법

### PDF 분석 엔드포인트

**POST** `/analyze-pdf`

- Content-Type: `multipart/form-data`
- Body: `file` (PDF 파일)

**응답 예시:**
```json
{
    "success": true,
    "markdown": "# 문서 제목\n\n## 핵심 개념 1\n...",
    "html_preview": "<h1>문서 제목</h1><h2>핵심 개념 1</h2>..."
}
```

## 문제 해결

1. Ollama 서버 시작 오류:
   - Ollama가 올바르게 설치되었는지 확인
   - 시스템 환경 변수에 Ollama가 등록되어 있는지 확인
   - 관리자 권한으로 실행 필요 여부 확인

2. EXAONE 모델 관련 오류:
   - 모델이 제대로 설치되었는지 확인: `ollama list`
   - 필요한 경우 모델 재설치: `ollama pull exaone3.5:7.8b`

## 라이선스

MIT License