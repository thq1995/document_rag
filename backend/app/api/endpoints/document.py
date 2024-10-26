from fastapi import APIRouter, UploadFile, Request, File, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from app.services.rag_service import RAGService
from pydantic import BaseModel
from langchain_openai import OpenAI
from app.core.config import Model;
from langchain.schema import HumanMessage
from langchain.chat_models import ChatOpenAI

router = APIRouter()
rag_service = RAGService()

class QueryRequest(BaseModel):
    question: str

@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    try:    
        await rag_service.process_documents(files)
        return {"message": "Documents processed successfully"}
    except HTTPException as e:
        return {"message": "Error processing documents"}

@router.post("/query")
async def query_documents(query: QueryRequest):
    try:
        response = await rag_service.get_response(query.question)
        return { 
            "answer": response["answer"],
        }
    except HTTPException as e:
        raise e  # Re-raise HTTP exceptions as-is
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error occurred")
    
@router.get("/test")
async def test():
    return {"message": "Hello World"}
    
