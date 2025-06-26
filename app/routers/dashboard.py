from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from app.core.schemas import schema
from app.core.models.database import DATABASE
from app.admin.auth import AuthHandler
from app.imports import *
import traceback
import os
import pandas as pd
import shutil

router = APIRouter()
database = DATABASE()
auth_handler = AuthHandler()

@router.post("/dashboard", tags=["Dashboard"])
def get_data(querydata:schema.DashbordSchema, username=Depends(auth_handler.auth_wrapper)):
    data = querydata.dict()
    transaction, summary, card = database.getdashboard_data(data)
    if transaction == -2:
        return {"status":"Failed"}
    elif transaction==0:
        return {'status':'No data available'}
    else:
        return {"transaction":transaction, "summary":summary, "card":card}

@router.post("/newdashboard", tags=["Dashboard"])
def get_data(querydata:schema.DashbordSchema_new, username=Depends(auth_handler.auth_wrapper)):
    data = querydata.dict()
    transaction, summary, card = database.getdashboard_data_new(data)
    if transaction == -2:
        return {"status":"Failed"}
    elif transaction==0:
        return {'status':'No data available'}
    else:
        return {"transaction":transaction, "summary":summary, "card":card}


@router.post('/updatevehicletype')#,  include_in_schema=False)
async def upload_vehicletypedata(file: UploadFile = File(...), username=Depends(auth_handler.auth_wrapper)):
    if file.content_type in ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
        file_location = os.path.join(data_dir, file.filename)
        
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        if file.content_type == 'text/csv':
            df = pd.read_csv(file_location, sep=',')
            tollfeedata = df.to_dict('records')
            database.updatevehicletypedata(tollfeedata)

        if file.content_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            df = pd.read_excel(file_location)
            tollfeedata = df.to_dict('records')
            database.updatevehicletypedata(tollfeedata)
    else:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail=f'File {file.filename} has unsupported extension type.')

    return {"status": 'Vehicle types data updated successfully!!!'}

@router.post('/updatevehiclesubtype')#,  include_in_schema=False)
async def upload_vehiclesubtypedata(file: UploadFile = File(...), username=Depends(auth_handler.auth_wrapper)):
    if file.content_type in ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
        file_location = os.path.join(data_dir, file.filename)
        
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        if file.content_type == 'text/csv':
            df = pd.read_csv(file_location, sep=',')
            tollfeedata = df.to_dict('records')
            database.updatevehiclesubtypedata(tollfeedata)

        if file.content_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            df = pd.read_excel(file_location)
            tollfeedata = df.to_dict('records')
            database.updatevehiclesubtypedata(tollfeedata)
    else:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail=f'File {file.filename} has unsupported extension type.')

    return {"status": 'Vehicle sub types data updated successfully!!!'}

@router.get('/getvehicletypes' , tags=["Dashboard"])
def get_vehicletypes(username=Depends(auth_handler.auth_wrapper)):
    vehicletypes = database.getvehicletypedata()
    return {'vehicletypes':vehicletypes}

@router.get('/getvehiclesubtypes' , tags=["Dashboard"])
def get_vehiclesubtypes(username=Depends(auth_handler.auth_wrapper)):
    vehicletypes = database.getvehiclesubtypedata()
    return {'vehiclesubtypes':vehicletypes}

@router.post('/updategroups')#,  include_in_schema=False)
async def upload_groupsdata(file: UploadFile = File(...), username=Depends(auth_handler.auth_wrapper)):
    if file.content_type in ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
        file_location = os.path.join(data_dir, file.filename)
        
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        if file.content_type == 'text/csv':
            df = pd.read_csv(file_location, sep=',')
            tollfeedata = df.to_dict('records')
            database.updatgroupsdata(tollfeedata)

        if file.content_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            df = pd.read_excel(file_location)
            tollfeedata = df.to_dict('records')
            database.updatgroupsdata(tollfeedata)
    else:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail=f'File {file.filename} has unsupported extension type.')

    return {"status": 'Groups data updated successfully!!!'}