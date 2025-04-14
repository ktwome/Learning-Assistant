import os
from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
import markdown
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="학습 보조 서버",
    description="PDF 문서를 분석하여 필요한 부분을 마크다운 형태로 변환하는 서버",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8080'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.on_event("startup")
async def startup_event():
    """
    서버 시작 시 Ollama 모델이 있는지 확인하고 없으면 다운로드
    (지금은 요약 체인 대신 직접 변환 방식을 쓰므로, 모델이 불필요하다면 제외 가능)
    """
    pass


def pdf_to_markdown(pdf_file: UploadFile) -> str:
    """
    PyPDF2를 활용하여 PDF 파일을 텍스트 추출 후
    간단한 규칙 기반으로 마크다운 형식에 맞춰 변환.
    """
    reader = PdfReader(pdf_file.file)
    md_pages = []

    for page_idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if not text:
            continue

        lines = text.splitlines()
        # 페이지 구분용 헤더
        page_header = f"\n\n# [Page {page_idx}]\n"
        md_lines = [page_header]

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 간단히 글머리 기호 붙여줌
            md_lines.append(f"- {line}")

        md_pages.append("\n".join(md_lines))

    # 여러 페이지를 구분선으로 연결
    full_md = "\n\n---\n\n".join(md_pages)
    return full_md


async def generate_markdown(pdf_file: UploadFile) -> str:
    """
    PDF 전체 텍스트를 마크다운으로 변환.
    (원본을 최대한 보존하여 길이 제한이 없도록)
    """
    md_text = pdf_to_markdown(pdf_file)
    # 후속 LLM 후처리가 필요하다면 여기서 호출
    return md_text


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
