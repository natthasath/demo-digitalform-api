from decouple import config
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse, Response
from fpdf import FPDF
from datetime import date
from io import BytesIO
import json
import glob
import os
import re

class DocumentService:
    def __init__(self):
        self.logo_default = config("LOGO_DEFAULT")
        self.font_default = config("FONT_DEFAULT")
        self.font_bold = config("FONT_BOLD")
        self.font_italic = config("FONT_ITALIC")
        self.family_default = config("FAMILY_DEFAULT")
        self.family_bold = config("FAMILY_BOLD")
        self.family_italic = config("FAMILY_ITALIC")
        self.job_no = 0
        self.day = str(date.today().day)
        self.month = str(date.today().month)
        self.year = str(date.today().year)
        self.line_max = 99
        self.line_half = 52
        self.line_sign = 44
        self.line_bracket = 38

    def generate_id(self):
        year = date.today().year + 543
        f = open('./app/json/request.json')
        data = json.load(f)
        f.close()
        default = str(year).split('25')[1] + '001'
        id = int(list(data)[-1]) + 1 if default in data else int(str(year).split('25')[1] + '001')
        self.job_no = id
        data[str(id)] = id
        json_object = json.dumps(data, indent=4)
        with open("./app/json/request.json", "w") as outfile:
            outfile.write(json_object)

        return self.job_no

    def text(self, key, value, line):
        underscore = ''
        pattern = re.compile(r"(?:[^\d\W]+)|\s")
        k = re.findall(pattern, key)
        v = re.findall(pattern, value) + re.findall(r"\d+", value)
        space = 6 if len(re.findall(r"\d+", value)) > 1 else 0
        limit = line - len(" ".join(k)) - len(" ".join(v)) + space

        for i in range(int(limit/2)):
            underscore += '_'

        exceed = '_' if int(limit % 2) is not 0 else ''
        check = str(len(" ".join(k)) + len(" ".join(v)) + len(underscore) + len(underscore) + len(exceed))
        return key + underscore + value + underscore + exceed

    def text_end(self, key, value, line, end):
        underscore = ''
        pattern = re.compile(r"(?:[^\d\W]+)|\s")
        k = re.findall(pattern, key)
        v = re.findall(pattern, value) + re.findall(r"\d+", value)
        e = re.findall(pattern, end)
        limit = line - len(" ".join(k)) - len(" ".join(v)) - len(" ".join(e))

        for i in range(int(limit/2)):
            underscore += '_'
        return key + underscore + value + underscore + end

    def text_usage(self, key, value, line):
        underscore = ''
        pattern = re.compile(r"(?:[^\d\W]+)|\s")
        k = re.findall(pattern, key)
        v = re.findall(pattern, value) + re.findall(r"\d+", value)
        space = 6 if len(re.findall(r"\d+", value)) > 1 else 0
        limit = line - len(" ".join(k)) - len(" ".join(v)) + space + (len(" ".join(v)) / 4)

        for i in range(int(limit/2)):
            underscore += '_'

        exceed = '_' if int(limit % 2) is not 0 else ''
        check = str(len(" ".join(k)) + len(" ".join(v)) + len(underscore) + len(underscore) + len(exceed))
        return key + underscore + value + underscore + exceed

    def section(self):
        underscore = ''
        for i in range(36):
            underscore += '_'
        return underscore

    def column(self):
        underscoreShort = ''
        for i in range(10):
            underscoreShort += '_'
        return underscoreShort

    def header(self, pdf):
        pdf.add_font(self.family_default, '', self.font_default, uni=True)
        pdf.set_font(self.family_default, '', 16)
        pdf.cell(0, 10, f'Job No. .....{self.job_no}.....', 0, 1, 'R')
        pdf.cell(145)
        pdf.cell(0, 10, f'วันที่ ...{self.day}.../...{self.month}.../...{self.year}...', 0, 1, 'L')

    def footer(self, pdf):
        pdf.add_font(self.family_default, '', self.font_default, uni=True)
        pdf.set_font(self.family_default, '', 16)
        pdf.set_y(-35)
        pdf.cell(0,0,'IDF-FM-IF-005 (25/10/2022)',0,1,'R')
        pdf.cell(0, 10,'ภายใน',0,1,'R')

    def subject(self, pdf):
        pdf.set_font(self.family_default, '', 16)
        pdf.cell(190,25,'',1,1,'L')
        pdf.image(self.logo_default,12,33,20,20,'JPG')
        pdf.cell(50)
        pdf.cell(0,-35,'แบบฟอร์มการขอใช้อินเทอร์เน็ต สำหรับผู้เข้าอบรม / สัมมนา',0,1,'L')
        pdf.cell(65)
        pdf.cell(0,50,'สำนักเทคโนโลยีดิจิทัลและสารสนเทศ',0,1,'L')

    def first(self, pdf, name, surname, position, department, phone, email):
        pdf.ln(-15)
        pdf.cell(190,35,'','LRB',1,'L')
        pdf.set_font(self.family_default, '', 16)
        pdf.cell(0,-60,'1. ข้อมูลผู้ประสานงานของหน่วยงาน',0,1,'L')
        pdf.set_font(self.family_default, '', 14)
        pdf.cell(10)
        pdf.cell(0,80,self.text('ชื่อ',name,self.line_half) + self.text('นามสกุล',surname,self.line_half),0,1,'L')
        pdf.cell(10)
        pdf.cell(0,-65,self.text('ตำแหน่ง',position,self.line_half) + self.text('หน่วยงาน',department,self.line_half),0,1,'L')
        pdf.cell(10)
        pdf.cell(0,80,self.text('หมายเลขโทรศัพท์',phone,self.line_half) + self.text_end('อีเมล',email.split('@')[0],self.line_half,'@nida.ac.th'),0,1,'L')

    def second(self, pdf, usage, account, start_date, end_date):
        pdf.ln(-40)
        pdf.cell(190,90,'','LRB',1,'L')
        pdf.set_font(self.family_default, '', 16)
        pdf.cell(0,-160,'2. รายละเอียดการขอรับบริการ',0,1,'L')
        pdf.set_font(self.family_default, '', 14)
        pdf.cell(10)
        pdf.cell(0,175,'มีความประสงค์ขอบัญชีผู้ใช้งานเครือข่ายอินเทอร์เน็ตสำหรับ',0,1,'L')
        pdf.cell(10)
        pdf.set_font(self.family_default, '', 14)
        pdf.cell(0,-165,self.text_usage('',usage,self.line_max),0,1,'L')
        pdf.cell(10)
        pdf.cell(0,180,self.text_end('จำนวนรายชื่อบัญชีผู้ใช้เครือข่ายอินเทอร์เน็ตที่ต้องการ',account,self.line_max,'รายชื่อ'),0,1,'L')
        pdf.cell(10)
        pdf.cell(0,-165,self.text('วันที่เริ่มใช้งาน',start_date,self.line_half) + self.text('ถึงวันที่',end_date,self.line_half) ,0,1,'L')
        pdf.cell(10)
        pdf.set_font(self.family_default, '', 14)
        pdf.cell(0,190,'หน้าที่ของผู้ขอบัญชีผู้ใช้เครือข่ายอินเทอร์เน็ตแบบชั่วคราว',0,1,'L')
        pdf.cell(10)
        pdf.set_font(self.family_default, '', 14)
        pdf.cell(0,-175,'1. ทำการเก็บข้อมูลเบื้องต้นของผู้ขอบัญชีเครือข่าย ได้แก่ ชื่อ นามสกุล เลขบัตรประชาชน เบอร์โทรศัพท์',0,1,'L')
        pdf.cell(10)
        pdf.cell(0,190,'2. ทำการเก็บข้อมูลบัญชีเครือข่ายเป็นอย่างดีเป็นระยะเวลาไม่น้อยกว่า 90 วัน หลังจากวันที่ใช้งานครั้งสุดท้าย',0,1,'L')
        pdf.cell(10)
        pdf.cell(0,-175,'3. หากมีผู้ร้องเรียนและขอรายชื่อ ผู้ใช้งาน ณ วัน ที่เกิดเหตุ ผู้ขอบัญชีหรือหน่วยงานที่ขอใช้งานจะต้องเป็นผู้ให้รายละเอียดของผู้ใช้งาน',0,1,'L')
        pdf.set_font(self.family_default, '', 14)
        pdf.cell(0,200,'หากมีข้อสงสัยในการกรอกข้อมูล ติดต่อสอบถามได้ที่ โทร 02-727-3783, 02-727-3262',0,1,'L')

    def third(self, pdf):
        pdf.ln(-95)
        pdf.cell(95,50,'','LRB',0,'L')
        pdf.cell(95,50,'','RB',1,'L')
        pdf.set_font(self.family_default, '', 16)
        pdf.cell(95,-90,'3. หน่วยงานผู้ขอรับบริการ(ผู้ประสานงาน)',0,0,'L')
        pdf.cell(0,-90,'4. สำนักเทคโนโลยีดิจิทัลและสารสนเทศ(ผู้ดำเนินการ)',0,1,'L')
        pdf.set_font(self.family_default, '', 14)
        pdf.ln(5)
        pdf.cell(10)
        pdf.cell(95,105,self.text('ลงนาม','',self.line_sign),0,0,'L')
        pdf.cell(0,105,self.text('ลงนาม','',self.line_sign),0,1,'L')
        pdf.cell(17)
        pdf.cell(95,-90,'( ' + self.text('','',self.line_bracket) + ' )',0,0,'L')
        pdf.cell(0,-90,'( ' + self.text('','',self.line_bracket) + ' )',0,1,'L')
        pdf.cell(10)
        pdf.cell(95,105,self.text('ตำแหน่ง','',self.line_sign),0,0,'L')
        pdf.cell(0,105,self.text('ตำแหน่ง','',self.line_sign),0,1,'L')
        pdf.cell(10)
        pdf.cell(95,-90,self.text('วันที่','',self.line_sign),0,0,'L')
        pdf.cell(0,-90,self.text('วันที่','',self.line_sign),0,1,'L')

    def pdf_generate(self, name, surname, position, department, phone, email, usage, account, start_date, end_date):
        self.generate_id()
        pdf = FPDF()
        pdf.add_page()
        self.header(pdf)
        self.subject(pdf)
        self.first(pdf, name, surname, position, department, phone, email)
        self.second(pdf, usage, account, start_date, end_date)
        self.third(pdf)
        self.footer(pdf)

        ret = pdf.output(dest='S')
        filename = str(self.job_no) + ".pdf"
        return StreamingResponse(BytesIO(ret), headers={'Content-Disposition': f'attachment; filename={filename}'})