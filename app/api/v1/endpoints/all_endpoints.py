from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.question import Question
from app.utils import genai, aipdf
from typing import Annotated
from PIL import Image
import io

router = APIRouter(prefix="", tags=['AI'])

@router.post('/ask')
async def ask_a_question(body : Question):
    question = body.question
    result = genai.ask_question(question)
    return {"answer" : result}

@router.post('/upload/image')
async def upload(image : Annotated[UploadFile, File()], question : Annotated[str, Form()] ) :
    contents = await image.read() 
    image_pil = Image.open(io.BytesIO(contents))
    result = genai.generate_content(question, image_pil)
    return {"answer" : result}

@router.post('/upload/pdf')
async def uploadPdf(pdfFiles : Annotated[list[UploadFile], File()], sessionId : Annotated[str, Form()]) :
    print(sessionId)
    try:
        if not pdfFiles:
            raise HTTPException(status_code=400, detail="No files uploaded")

        pdfText = aipdf.get_pdf_text(pdfFiles)

        chunks = aipdf.get_chunks_from_text(pdfText)
        
        result = aipdf.get_vector_store(chunks, sessionId=sessionId)
        if "error" in result:
            return JSONResponse(status_code=500, content={"error": result["error"]})
        
        return {"message": "File has been loaded successfully"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"An error occurred: {str(e)}"})



@router.post('/ask/pdf')
async def answerQuestionFromPdf(body: Question):
    result = aipdf.user_input(body.question, sessionId=body.sessionId)
    return {"answer" : result['output_text']}




