import os
from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
import markdown
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import asyncio

# ============================
# FastAPI 생애주기 관련 세팅
# ============================

def start():
    print('백엔드 서버가 실행되었습니다.')

def shutdown():
    print('백엔드 서버가 종료되었습니다.')

@asynccontextmanager
async def lifespan(app: FastAPI):
    start()
    yield
    shutdown()


# ============================
# FastAPI 사전 설정 정의
# ============================

# 환경변수 호출
load_dotenv()

# FastAPI 세팅
app = FastAPI(
    title="학습 보조 서버",
    description="PDF 문서를 분석하여 필요한 부분을 마크다운 형태로 변환하는 서버",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8080'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


# ============================
# LLM 세팅
# ============================

MODEL_NAME = "exaone3.5:7.8b" 
OLLAMA_URL = "http://localhost:11434"

llm = OllamaLLM(
    model=MODEL_NAME,
    base_url=OLLAMA_URL,
    temperature=0,
    max_tokens=1024
)

page_prompt = PromptTemplate(
    input_variables=["text", "page"],
    template="""
        당신은 PDF 슬라이드를 구조화된 마크다운으로 정돈하는 도우미입니다.

        규칙
        1. 첫 줄을 그 페이지의 핵심 소제목으로 하여 `## 소제목` 형식으로 작성.
        - 적절한 소제목이 없다면 핵심 키워드를 5단어 이내로 생성.
        2. 원문 순서를 존중하되, 불필요한 공백·중복·풋터·슬라이드 번호를 제거.
        3. 글머리표(•, -, ‣)는 `-` 로 통일, 번호 목록은 유지.
        4. 표/코드는 ```markdown 블록```으로 감싸지 말고 그대로 두기.
        5. PDF 문서 변환외의 불필요한 첨언을 하지마세요. (ex. 이 마크다운 형식은... 절대 금지)

        정돈되지 않은 PDF 슬라이드:

        {text}

        변환된 마크다운:
    """
)

# 3개로 LLM 동시 호출 제한
sem = asyncio.Semaphore(3)


# ============================
# API 관련 함수들
# ============================

# PDF 페이지 -> 페이지 별 텍스트 리스트
def extract_pages(file: UploadFile) -> List[str]:
    """PDF 페이지별 원문 텍스트 리스트 반환"""
    file.file.seek(0)
    reader = PdfReader(file.file)

    return [p.extract_text() or "" for p in reader.pages]

# 페이지 텍스트 -> 구조화된 Markdown
async def refine_page(idx: int, raw: str) -> str:
    """LLM으로 페이지 하나를 구조화 MD로 변환"""
    if not raw.strip():
        return ""
    
    prompt = page_prompt.format(text=raw, page=str(idx + 1))
    async with sem:
        md = await llm.apredict(prompt)   # OllamaLLM 비동기 호출

    return f"\n{md.strip()}"

# 통합 과정
async def generate_markdown(pdf_file: UploadFile) -> str:
    """
    1) PDF 페이지 추출
    2) 각 페이지를 LLM으로 구조화
    3) 구분선(---)으로 연결해 하나의 MD 반환
    """
    pages_raw = extract_pages(pdf_file)

    tasks = [
        refine_page(i, text) for i, text in enumerate(pages_raw)
    ]
    md_pages = await asyncio.gather(*tasks)      # 병렬 처리
    full_md = "\n\n---\n\n".join(md for md in md_pages if md)
    return full_md


# ============================
# 응답 스키마 모델 정의
# ============================

class PreProcessPDFSuccessResponse(BaseModel):
    """
    analyze_pdf response가 성공적일 경우의 스키마 모델
    """
    success: bool
    markdown: str
    html_preview: str


class PreProcessPDFFailResponse(BaseModel):
    """
    analyze_pdf response가 실패했을 경우의 스키마 모델
    """
    success: bool
    error: str



# ============================
# 실제 API 처리 함수들
# ============================

@app.post(
    "/preprocess-pdf",
    response_model=PreProcessPDFSuccessResponse,
    responses={
        500: {"model": PreProcessPDFFailResponse, "description": "내부 서버 오류"}
    },
)
async def preprocess_pdf(file: UploadFile = File(...)):
    """
    PDF 텍스트를 마크다운으로 변환하여 반환합니다.
    """
    try:
        md_text = await generate_markdown(file)
        html_preview = markdown.markdown(md_text)
        return {
            "success": True,
            "markdown": md_text,
            "html_preview": html_preview
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )
