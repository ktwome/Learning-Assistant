import os, uuid, pathlib, asyncio
from datetime import datetime
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, status, Response
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from PyPDF2 import PdfReader

from sqlmodel import SQLModel, Field, create_engine, Session, select
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

from pydantic import BaseModel 

# ──────────────────────────────
# Lifespan
# ──────────────────────────────
def start():    print("백엔드 서버가 실행되었습니다.")
def shutdown(): print("백엔드 서버가 종료되었습니다.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    start()
    yield
    shutdown()

# ──────────────────────────────
# FastAPI & CORS
# ──────────────────────────────
load_dotenv()

app = FastAPI(
    title="학습 보조 서버",
    description="PDF를 Markdown 으로 변환하고 보관하는 API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────
# Database (SQLite → 교체 가능)
# ──────────────────────────────
engine = create_engine("sqlite:///./db.sqlite3")
DATA_DIR = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)

class MdDoc(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    pdf_name: str
    title: str 
    md_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

SQLModel.metadata.create_all(engine)

# ──────────────────────────────
# LLM 세팅
# ──────────────────────────────
llm = OllamaLLM(
    model=os.getenv("MODEL_NAME", "exaone3.5:7.8b"),
    base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    temperature=0,
    max_tokens=1024,
)

page_prompt = PromptTemplate(
    input_variables=["text", 'page'],
    template="""
당신은 대학 강의 슬라이드를 **깔끔한 마크다운**으로 정돈하는 전문가입니다.

──────────────────────────
💡 **변환 규칙 (필수)**  
1. **제목 추출**
   1) 슬라이드 안에서 ‘강의명·장 제목·단원 제목’처럼 가장 상위 의미를 갖는 구절을 찾아
      `## 제목` 1줄로 작성한다.  
   2) 만약 제목이 슬라이드 하단이나 중간에 있어도 **반드시 맨 위**로 이동한다.  
   3) 5 단어 이하, 불필요한 번호·영문 “Page”·학교명·저자명 제거.

2. **본문 정돈**
   - 하위 소제목이 있으면 `### 소제목` 형태로 유지한다.  
   - 글머리 기호는 모두 `-` 로 통일, 번호 목록(1. 2. 3.)은 유지한다.  
   - 연속 빈 줄은 하나로 줄인다.

3. **잡음 제거 (삭제 대상)**
   - “Page \d+”, “DAEJEON UNIVERSITY”, “Copyright ⓒ …” 등  
   - 슬라이드 번호·풋터·머리글·로고·이메일·날짜·저자 직위  
   - “강의 운영 안내”처럼 **제목과 중복**되는 구문이 본문에 또 나오면 삭제.

4. **포맷**
   - 표나 코드 블록은 ``` 없이 **그대로** 둔다.  
   - 출력은 **마크다운 본문만** 제공하며, 추가 설명·서문·후문 금지.

──────────────────────────
다음은 원본 슬라이드 텍스트입니다.  
(이미 페이지 {page} 로 구분되어 있으므로 추가 페이지 표시는 하지 마세요)

{text}

──────────────────────────
이제 위 내용을 규칙에 맞춰 정돈된 **마크다운**으로만 출력하세요.
"""
)

sem = asyncio.Semaphore(3)  # 동시 LLM 호출 제한

# ──────────────────────────────
# 내부 유틸
# ──────────────────────────────
import re
TITLE_RE = re.compile(r"^\s*##\s+(.*)", re.MULTILINE)

def extract_title(md_text: str, fallback: str) -> str:
    """첫 `##` 헤더를 제목으로 사용, 없으면 파일명으로 대체"""
    m = TITLE_RE.search(md_text)
    return m.group(1).strip() if m else fallback

def extract_pages(file: UploadFile) -> List[str]:
    file.file.seek(0)
    reader = PdfReader(file.file)
    return [p.extract_text() or "" for p in reader.pages]

async def refine_page(idx: int, raw: str) -> str:
    if not raw.strip():
        return ""
    prompt = page_prompt.format(text=raw, page=str(idx + 1))
    async with sem:
        md = await llm.apredict(prompt)
    return md.strip()

async def pdf_to_markdown(file: UploadFile) -> str:
    pages_raw = extract_pages(file)
    tasks = [refine_page(i, t) for i, t in enumerate(pages_raw)]
    md_pages = await asyncio.gather(*tasks)
    return "\n\n---\n\n".join(p for p in md_pages if p)

# ──────────────────────────────
# Pydantic 응답 모델
# ──────────────────────────────
class PdfMeta(BaseModel):
    id: str
    pdf_name: str
    title: str  
    created_at: datetime

class CreatePdfResp(BaseModel):
    success: bool
    id: str
    pdf_name: str
    title: str
    created_at: datetime

class MarkdownResp(BaseModel):
    success: bool
    markdown: str

class ErrorResp(BaseModel):
    success: bool
    error: str

# ──────────────────────────────
# API 엔드포인트
# ──────────────────────────────
@app.post(
    "/pdfs",
    response_model=CreatePdfResp,
    responses={500: {"model": ErrorResp}},
)
async def create_pdf(file: UploadFile = File(...)):
    """PDF 업로드 → 페이지별 Markdown 변환 → 저장"""
    try:
        md_text = await pdf_to_markdown(file)

        # 제목 추출
        title = extract_title(md_text, pathlib.Path(file.filename).stem)

        # 저장
        doc_id = uuid.uuid4().hex
        md_path = DATA_DIR / f"{doc_id}.md"
        md_path.write_text(md_text, encoding="utf-8")

        with Session(engine) as db:
            db.add(
                MdDoc(
                    id=doc_id,
                    pdf_name=file.filename,
                    title=title,          # ★ 저장
                    md_path=str(md_path),
                )
            )
            db.commit()

        return {
            "success": True,
            "id": doc_id,
            "pdf_name": file.filename,
            "title": title,
            "created_at": datetime.utcnow()
        }
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@app.get("/pdfs", response_model=List[PdfMeta])
def list_pdfs():
    '''
    전체 PDF 파일을 조회
    '''
    with Session(engine) as db:
        return db.exec(select(MdDoc).order_by(MdDoc.created_at.desc())).all()


@app.get(
    "/pdfs/{pdf_id}/markdown",
    response_model=MarkdownResp,
    responses={404: {"model": ErrorResp}},
)
def get_markdown(pdf_id: str):
    '''
    pdf_id에 해당하는 마크다운을 조회
    '''
    with Session(engine) as db:
        doc = db.get(MdDoc, pdf_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Not found")

    md_text = pathlib.Path(doc.md_path).read_text(encoding="utf-8")
    return {"success": True, "markdown": md_text}


@app.get(
    "/pdfs/{pdf_id}/download",
    responses={404: {"model": ErrorResp}},
)
def download_markdown(pdf_id: str):
    '''
    pdf_id에 해당하는 마크다운 파일을 저장
    '''
    with Session(engine) as db:
        doc = db.get(MdDoc, pdf_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Not found")

    return FileResponse(
        path=doc.md_path,
        media_type="text/markdown",
        filename=f"{pathlib.Path(doc.pdf_name).stem}.md",
    )

@app.delete(
    "/pdfs/{pdf_id}",
    status_code=status.HTTP_204_NO_CONTENT,   # 204 No Content
    responses={404: {"model": ErrorResp}},
)
def delete_pdf(pdf_id: str):
    """
    pdf_id에 해당하는 Markdown 파일과 메타데이터 삭제
    """
    with Session(engine) as db:
        doc = db.get(MdDoc, pdf_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Not found")

        # ① DB 레코드 삭제
        db.delete(doc)
        db.commit()

    # ② 물리 파일 삭제(예외 무시)
    try:
        pathlib.Path(doc.md_path).unlink(missing_ok=True)
    except Exception:
        pass

    # 204 응답
    return Response(status_code=status.HTTP_204_NO_CONTENT)