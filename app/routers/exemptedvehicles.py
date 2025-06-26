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

@router.post('/getexemptedvehicles', tags=["Exempted Vehicles"])
def get_exemptedvehicles_data(request: schema.GetDataSchema, username=Depends(auth_handler.auth_wrapper)):
    # print(username)
    company = request.dict().get('company')
    location = request.dict().get('location')
    tollid = request.dict().get('tollid')
    exemptedvehicles = database.getexemptedveicledata(company, location, tollid)
    return {'exemptedvehicles':exemptedvehicles}

@router.post("/addexemptedvehicle", tags=["Exempted Vehicles"])
async def add_exemptedvehicle(data: schema.ExemptedvehicleSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    if re.match('^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{3,4}$', data.vehicleno.replace(" ", '')):
        resp = database.addexemptedvehicle(data.dict())
        if resp == -2:
            return {"status":"Failed"}
        else:
            if resp:
                return {'id':str(resp), "status": 'Exempted Vehicle added successfully!!!'}
            else:
                return {"status":"Exempted Vehicle records already present."}
    else:
        return {"status":"Enter correct vehicle number!"}

@router.post("/editexemptedvehicle", tags=["Exempted Vehicles"], include_in_schema=False)
def get_exemptedvehicle_data(request: schema.EditExemptedvehicleSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    company = request.dict().get('company')
    location = request.dict().get('location')
    tollid = request.dict().get('tollid')
    vehicleno = request.dict().get('vehicleno')
    exemptedvehicle = database.getexemptedveicledataforedit(company, location, tollid, vehicleno)
    return {'exemptedvehicledata':exemptedvehicle}


@router.post("/saveexemptedvehicle", tags=["Exempted Vehicles"])
async def save_exemptedvehicle(data: schema.SaveExemptedvehicleSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    if re.match('^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{3,4}$', data.vehicleno):    
        resp = database.saveexemptedvehicledata(data.dict())
        if resp == 0:
            return {"status": 'Exempted vehicle data updated successfully!!!'}
        else:
            return {"status":"Failed"}
    else:
        return {"status":"Enter correct vehicle number!"}


@router.post("/deleteexemptedvehicle", tags=["Exempted Vehicles"])
async def delete_exemptedvehicle(data: schema.DeleteexemptedvehicleSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    resp = database.deleteexemptedvehicle(data.dict())
    if resp == -2:
        return {"status":"Failed"}
    else:
        if resp:
            return {'Number of records deleted':str(resp), "status": 'Exempted Vehicles deleted successfully!!!!!!'}
        else:
            return {"status":"Exempted Vehicle does not exist."}

@router.post('/update_exemptedvehicles', tags=["Exempted Vehicles"], include_in_schema=True)
async def upload_exemptedvehicles(data: schema.UploadExemptedVehiclesData = Depends(),file: UploadFile = File(...), username=Depends(auth_handler.auth_wrapper)):
    # job_id = str(uuid.uuid4())
    # job_path = os.path.join(vid_dir, job_id)
    # if os.path.isdir(job_path):
    #     shutil.rmtree(job_path)
    # os.makedirs(job_path)
    # unsupportedfiles = []
    
    # for file in files:
    # print(data)
    print(file.content_type)
    if file.content_type in ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
        file_location = os.path.join(data_dir, file.filename)
        
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        if file.content_type == 'text/csv':
            df = pd.read_csv(file_location, sep=',')
            df.loc[:,'vehicleno'] = df['vehicleno'].str.replace(' ', '')
            df.loc[:,'company'] = data.dict().get('company')
            df.loc[:,'location'] = data.dict().get('location')
            df.loc[:,'tollid'] = data.dict().get('tollid')
            exemptvehicle = df.to_dict('records')
            # print(exemptvehicle)
            database.updateexemptedvehicle(exemptvehicle)

        if file.content_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            df = pd.read_excel(file_location)
            df.loc[:,'vehicleno'] = df['vehicleno'].str.replace(' ', '')
            df.loc[:,'company'] = data.dict().get('company')
            df.loc[:,'location'] = data.dict().get('location')
            df.loc[:,'tollid'] = data.dict().get('tollid')
            exemptvehicle = df.to_dict('records')
            database.updateexemptedvehicle(exemptvehicle)
    else:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail=f'File {file.filename} has unsupported extension type.')
    return {"status": 'Monthly Pass vehicles data updated successfully!!!'}