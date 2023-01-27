from fastapi import Form
from pydantic import BaseModel, Field, EmailStr, SecretStr
from typing import List, Union
import inspect

def form_body(cls):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(default = arg.default) if arg.default is not inspect._empty else Form(...))
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls

@form_body
class I_SectionSchema(BaseModel):
    name: str = Field(...)
    surname: str = Field(...)
    position: str = Field(...)
    department: str = Field(...)
    phone: str = Field(...)
    email: EmailStr = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "name": "Alan",
                "surname": "Turing",
                "position": "นักวิชาการคอมพิวเตอร์ปฏิบัติการ",
                "department": "สำนักเทคโนโลยีสารสนเทศ",
                "phone": "027273729",
                "email": "username@nida.ac.th",
            }
        }

@form_body
class II_SectionSchema(BaseModel):
    usage: str = Field(...)
    account: str = Field(...)
    start_date: str = Field(...)
    end_date: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "usage": "ใช้สำหรับสร้างเว็บไซต์คณะหน่วยงาน",
                "account": "1",
                "start_date": "1",
                "end_date": "1",
            }
        }