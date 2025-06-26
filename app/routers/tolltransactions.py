from fastapi import APIRouter, Depends, Body
from fastapi.responses import FileResponse
from app.core.schemas import schema
from app.core.models.database import DATABASE
from app.admin.auth import AuthHandler
from app.imports import *

router = APIRouter()
database = DATABASE()
auth_handler = AuthHandler()



@router.post('/gettransactiondetails',  tags = ['Toll Transactions'])
def get_vehicle_data(request: schema.TransactionTableSchema, username=Depends(auth_handler.auth_wrapper)):
    company = request.dict().get('company')
    location = request.dict().get('location')
    tollid = request.dict().get('tollid')
    laneno = request.dict().get('laneno')
    vehicle_details = database.vehicle_details(company, location, tollid, laneno)
    return {'vehicle_details':vehicle_details}

@router.post('/get_image',  tags = ['Toll Transactions'])
def send_file(request: schema.filepath, username=Depends(auth_handler.auth_wrapper)):
    f_path = request.dict().get('filepath')
    file_path = f"{base_dir}/{f_path}"
    print(file_path)
    return FileResponse(file_path)

@router.post('/get_videoclip',  tags = ['Toll Transactions'])
async def send_videoclip(request: schema.filepath, username=Depends(auth_handler.auth_wrapper)):
    f_path = request.dict().get('filepath')
    file_path = f"{base_dir}/{f_path}"
    return FileResponse(file_path, media_type="video/mp4")