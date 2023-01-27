from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from app.models.model_document import I_SectionSchema, II_SectionSchema
from app.services.service_document import DocumentService

router = APIRouter(
    prefix="/document",
    tags=["DOCUMENT"],
    responses={404: {"message": "Not found"}}
)

@router.post("/pdf")
async def pdf_generate(data: I_SectionSchema = Depends(I_SectionSchema), params: II_SectionSchema = Depends(II_SectionSchema)):
    return DocumentService().pdf_generate(data.name, data.surname, data.position, data.department, data.phone, data.email, params.usage, params.account, params.start_date, params.end_date)

@router.post("/date")
async def pdf_generate():
    return DocumentService().generate_id()