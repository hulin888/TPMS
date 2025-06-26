import shutil
from fastapi import APIRouter, Depends, Body, UploadFile, File
from fastapi import status, HTTPException
from app.imports import data_dir
from app.core.schemas import schema
from app.core.models.database import DATABASE
from app.admin.auth import AuthHandler
import traceback
import re
import os
import shutil
import pandas as pd


router = APIRouter()
database = DATABASE()
auth_handler = AuthHandler()



@router.post('/getmonthlypassvehicles' , tags=["Monthly Pass"])
def get_monthlypassvehicles_data(request: schema.GetDataSchema, username=Depends(auth_handler.auth_wrapper)):
    print(username)
    company = request.dict().get('company')
    location = request.dict().get('location')
    tollid = request.dict().get('tollid')
    monthlypassvehicles = database.getmonthlypassvehicledata(company, location, tollid)
    return {'monthlypassvehicles':monthlypassvehicles}

@router.post("/addmonthlypassvehicle", tags=["Monthly Pass"])
async def add_monthlypassvehicle(data: schema.MonthlyPassSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    if re.match('^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{3,4}$', data.vehicleno.replace(" ", '')):
        resp = database.addmonthlypassvehicle(data.dict())
        if resp == -2:
            return {"status":"Failed"}
        else:
            if resp:
                return {'id':str(resp), "status": 'Monthly Pass Vehicle added successfully!!!!!!'}
            else:
                return {"status":"Monthly Pass Vehicle records already present."}
    else:
        return {"status":"Enter correct vehicle number!"}


@router.post("/editmonthlypassvehicle", tags=["Monthly Pass"], include_in_schema=False)
def get_monthlypassvehicle_data(request: schema.EditMonthlyPassSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    company = request.dict().get('company')
    location = request.dict().get('location')
    tollid = request.dict().get('tollid')
    vehicleno = request.dict().get('vehicleno')
    monthlypassvehicle = database.getmonthlypassveicledataforedit(company, location, tollid, vehicleno)
    return {'monthlypassvehicledata':monthlypassvehicle}



@router.post("/savemonthlypassvehicle", tags=["Monthly Pass"])
async def save_monthlypassvehicle(data: schema.SaveMonthlyPassSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    if re.match('^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{3,4}$', data.vehicleno):
        resp = database.savemonthlypassvehicle(data.dict())
        if resp == 0:
            return {"status": 'Monthly Pass vehicle data updated successfully!!!'}
        else:
            return {"status":"Failed"}
    else:
        return {"status":"Enter correct vehicle number!"}



@router.post("/deletemonthlypassvehicle", tags=["Monthly Pass"])
async def delete_monthlypassvehicle(data: schema.DeletemonthlypassvehicleSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    resp = database.deletemonthlypassvehicle(data.dict())
    if resp == -2:
        return {"status":"Failed"}
    else:
        if resp:
            return {'Number of records deleted':str(resp), "status": 'Monthly Pass Vehicles deleted successfully!!!!!!'}
        else:
            return {"status":"Monthly Pass Vehicle does not exist."}


@router.post('/update_monthlypassvehicles', tags=["Monthly Pass"], include_in_schema=False)
async def upload_tollfee(file: UploadFile = File(...)):
    # job_id = str(uuid.uuid4())
    # job_path = os.path.join(vid_dir, job_id)
    # if os.path.isdir(job_path):
    #     shutil.rmtree(job_path)
    # os.makedirs(job_path)
    # unsupportedfiles = []
    
    # for file in files:
    print(file.content_type)
    if file.content_type in ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
        file_location = os.path.join(data_dir, file.filename)
        
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        if file.content_type == 'text/csv':
            df = pd.read_csv(file_location, sep=',')
            exemptvehicle = df.to_dict('records')
            database.updatemonthlypassvehicle(exemptvehicle)

        if file.content_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            df = pd.read_excel(file_location)
            exemptvehicle = df.to_dict('records')
            database.updatemonthlypassvehicle(exemptvehicle)
    else:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail=f'File {file.filename} has unsupported extension type.')
    return {"status": 'Monthly Pass vehicles data updated successfully!!!'}