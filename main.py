from typing import Union
from typing import List, Annotated

# FastAPI
from fastapi import FastAPI, Request, HTTPException, Depends, File, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os, asyncio

# import SQLAlchemy from provider
import provider.models
from provider.db import engine, SessionLocal
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import update

# import function
from function.docxauto import Doc_Auto

# Fonnte Connection
from provider.send_rq import ResponseHandler
tw = ResponseHandler()

# create database column
provider.models.Base.metadata.create_all(bind=engine)

# activate database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# activate FastAPI
db_dependency = Annotated[Session, Depends(get_db)]
Session = sessionmaker(bind=engine)
word = Doc_Auto(db_con=Session(), model=provider.models)
app = FastAPI()

# Create a directory to store uploaded files
UPLOAD_DIRECTORY = "public"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Mount the public directory to serve static files
app.mount("/files", StaticFiles(directory=UPLOAD_DIRECTORY), name="files")

# ==================================================
# FastAPI endpoints
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/message")
def read_root():
    return {"Hello": "World"}


@app.post("/message")
async def message_handler(req: Request, db: db_dependency):
    incoming_payload = await req.json()
    protocol = req.url.scheme
    host = req.headers["host"]

    # sumber
    message_body = incoming_payload.get('pesan','')
    print(message_body)
    nomor_hp = incoming_payload.get('pengirim', '')
    name = incoming_payload.get('name', 'User')

    # response_message = "Received message: " + message_body
    user_activity = db.query(provider.models.user_activity).filter_by(no_hp = nomor_hp).first()

    # cek aktivitas user & greeting
    if user_activity == 'None' or user_activity == None:
        tw.sendMsg(nomor_hp, f"Welcome to OohBali UK chatbot, {name}! Let's try to send 'menu' to start.")
        new_user = provider.models.user_activity(no_hp=nomor_hp, activity='menu')
        db.add(new_user)
        db.commit()
    
    if user_activity.no_hp == nomor_hp:
        # membuat form otomatis
        if user_activity.activity == 'menu':
            user_activity.activity = 'decision'
            db.commit()
            tw.sendMsg(nomor_hp, f"*[OOHBALI UK CHATBOT MENU]*\nHow can we help you, {name}?\n1. Information about Ooh Bali UK \n2. Find My Job")
            return {"success": True}
        
        if user_activity.activity == 'decision':
            # if else based on choice
            if message_body == "1" or 'information' in message_body:
                user_activity.activity = f'service_1'
                db.commit()
                tw.sendMsg(nomor_hp, f"*[OOH BALI UK INFORMATION MENU]*\nWhat would you like to know about Ooh Bali UK?\n1. About OOH Bali UK\n2. Vision and Mission\n3. Key Features\n4. Services")                
                return {"success": True}

            if message_body == "2" or 'find' in message_body:
                user_activity.activity = f'service_2#find_job#name#{nomor_hp}'
                db.commit()
                # tw.sendMsg(nomor_hp, f"*[OOH BALI UK FIND JOB SERVICE]*\nSystem is still in the middle of maintenance. We apologize for the inconvenience. Please send 'menu' to return to the main menu.")                
                tw.sendMsg(nomor_hp, "Welcome the the OOHBali UK Job Find Service! From now on, we will do our best to assist you in finding the best job for you. First of all, may we have your name, please?")
                return {"success": True}
            
            if message_body not in ['1','2', 'information', 'register', 'menu']:
                user_activity.activity = 'decision'
                db.commit()
                tw.sendMsg(nomor_hp, f"Sorry, there's no available service from the chosen option. Please send another choice based on the available options in the menu.")
                return {"success": True}

        # FAQ
        if user_activity.activity.startswith('service_1'):
            act = user_activity.activity.split('#')
            back = ("_(Please send 'menu' to go back to the main menu.)_")
            # TENTANG OOH BALI UK
            if message_body == '1' or 'what is' in message_body or 'about oohbali' in message_body:
                tw.sendMsg(nomor_hp, f"*[ABOUT OOH BALI UK]*\nOOH Bali UK LTD is a globally recognized workforce solutions provider, offering comprehensive staffing services to meet the diverse needs of businesses across international borders. With a focus on sourcing talent from countries such as Indonesia, India, and other Asian nations, we specialize in connecting skilled professionals with opportunities worldwide.\n\n{back}")            
                user_activity.activity = 'service_1#faq#finish'
                db.commit()
                return {"success": True}
            # TENTANG VISI DAN MISI
            if message_body == '2' or 'vision' in message_body:
                tw.sendMsg(nomor_hp, f"*[OOH BALI UK VISION AND MISSION]*\nOur vision is to be the preferred partner for organizations seeking innovative and reliable workforce solutions on a global scale. We are committed to delivering excellence in recruitment, fostering cross-cultural collaboration, and empowering businesses to thrive in an increasingly interconnected world.\n\n{back}")
                user_activity.activity = f'service_1#faq#finish'
                db.commit()
                return {"success": True}
            # TENTANG FITUR
            if message_body == '3' or 'features' in message_body:
                tw.sendMsg(nomor_hp, f"*[OOH BALI UK KEY FEATURES]*\n*Diverse Talent Pool*\nWe boast a diverse talent pool comprising skilled professionals from various countries and cultural backgrounds, enabling us to meet the unique requirements of our clients across industries\n\n*Global Reach*\nOur global footprint allows us to access talent from around the world and connect them with opportunities in different regions, facilitating international mobility and fostering cross-border collaboration\n\n*Cutting-Edge Technology*\nWe leverage advanced recruitment technologies and data analytics to streamline our processes, ensuring efficiency, transparency, and accuracy in talent acquisition and management\n\n*Client-Centric Approach*\nWe prioritize client satisfaction and strive to exceed expectations by delivering personalized solutions tailored to their specific needs and objectives\n\n{back}")
                user_activity.activity = f'service_1#faq#finish'
                db.commit()
                return {"success": True}
            if message_body == '4' or 'services' in message_body:
                tw.sendMsg(nomor_hp, f"*[OOH BALI UK SERVICES]*\n*International Recruitment and Placement*\nLeveraging our extensive network and expertise, we specialize in recruiting skilled professionals from diverse cultural backgrounds to meet the specific needs of our clients worldwide.\n\n*Cross Cultural Training*\nWe provide comprehensive training programs to ensure seamless integration and effective communication among multinational teams, fostering a harmonious work environment.\n\n*Visa and Immigration Support*\nOur dedicated team assists candidates with visa and immigration procedures, ensuring compliance with local regulations and facilitating a smooth transition to their country of work\n\n*Onboarding and Integration*\nWe offer personalized support to both employers and employees during the onboarding process, fostering a sense of belonging and maximizing productivity from day one.\n\n*Compliance and Legal Advisory*\nWith a deep understanding of international labor laws and regulations, we provide expert guidance to clients on compliance matters, minimizing legal risks and liabilities.\n\n{back}")
                user_activity.activity = f'service_1#faq#finish'
                db.commit()
                return {"success": True}
            # BACK
            if act[2] == 'finish' and message_body == 'return':
                user_activity.activity = 'service_1'
                db.commit()
                tw.sendMsg(nomor_hp, f"What would you like to know about Ooh Bali UK?\n1. About OOH Bali UK\n2. Vision and Mission\n3. Key Features\n4. Services")                
                return {"success": True}
            
            # ERROR MESSAGE
            if message_body not in ['1', '2', '3', '4', 'return', 'menu']:
                tw.sendMsg(nomor_hp, "Sorry, there's no available service from the chosen option. Please send another choice based on the available menu.")
                return {"success": True}
        
        if user_activity.activity.startswith('service_2#'):
            act_job = user_activity.activity.split('#')
            back = ("_(Please send 'return' to go back to FAQs or 'menu' to go back to the main menu.)_")
            # input name done
            if act_job[2] == 'name':
                new_jobseeker = provider.models.find_job(name=message_body, id_find_job = int(user_activity.id))
                db.add(new_jobseeker)
                user_activity.activity = f'service_2#find_job#job#{new_jobseeker.id_find_job}'
                db.commit()
                tw.sendMsg(nomor_hp, f"Thank you! Do you have any ideal or dream job you'd love to apply?")
                return {"success": True}
            # input job
            if act_job[2] == 'job':
                existing_job_form = db.query(provider.models.find_job).filter_by(id_find_job = act_job[3]).first()
                existing_job_form.role = message_body
                user_activity.activity = f'service_2#find_job#location#{act_job[3]}'
                db.commit()
                tw.sendMsg(nomor_hp, f"Thank you! Which location would be your ideal choice for work?")
                return {"success": True}
            # input location
            if act_job[2] == 'location':
                existing_job_form = db.query(provider.models.find_job).filter_by(id_find_job = act_job[3]).first()
                existing_job_form.role = message_body
                user_activity.activity = f'service_2#find_job#email#{act_job[3]}'
                db.commit()
                tw.sendMsg(nomor_hp, f"To give you the detailed information about the job matches, would you love them to be sent directly to your mailbox? Kindly provide your email below.\n(Send - to show the job matches in this conversation instead)")
                return {"success": True}
            # input email address
            if act_job[2] == 'email':
                if message_body == '-':
                    existing_job_form = db.query(provider.models.find_job).filter_by(id_find_job = act_job[3]).first()
                    existing_job_form.role = message_body
                    user_activity.activity = f'service_2#find_job#finish#{act_job[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Finish. (still in maintenance).\n\n{back}")
                    return {"success": True}
                else:
                    existing_job_form = db.query(provider.models.find_job).filter_by(id_find_job = act_job[3]).first()
                    existing_job_form.role = message_body
                    user_activity.activity = f'service_2#find_job#finish#{act_job[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Finish. (still in maintenance).\n\n{back}")
                    return {"success": True}
                
        if message_body == 'menu' or message_body == 'Menu':
            tw.sendMsg(nomor_hp, f"*[OOHBALI UK CHATBOT MENU]*\nHow can we help you, {name}?\n1. Information about Ooh Bali UK \n2. Find My Job")
            user_activity.activity = 'decision'
            db.commit()
            return {"success": True}

    return {"success": True}
    

