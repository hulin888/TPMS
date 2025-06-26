from fastapi import APIRouter, Depends, Body, UploadFile, File
from fastapi import status, HTTPException
from app.imports import data_dir
from app.core.schemas import schema
from app.core.models.database import DATABASE
from app.admin.auth import AuthHandler
import traceback
import shutil
import os
import pandas as pd

router = APIRouter()
database = DATABASE()
auth_handler = AuthHandler()

@router.post('/gettollfee', tags=["Toll Fee"])
def get_tollfee_data(request: schema.GetDataSchema, username=Depends(auth_handler.auth_wrapper)):
    company = request.dict().get('company')
    location = request.dict().get('location')
    tollid = request.dict().get('tollid')
    tollfeedata = database.gettollfeedata(company, location, tollid)
    return {'tollfeedata':tollfeedata}

@router.post("/addtollfee", tags=["Toll Fee"])
async def add_tollfee(data: schema.TollFeeSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    if data.singlejourny==0 or data.retunjourney==0 or data.monthlypass==0 or data.retunjourney==0:
        return {"status":"Toll Fee rates can not be zero."}
    resp = database.addtollfeedata(data.dict())
    if resp == -2:
        return {"status":"Failed"}
    elif resp ==1:
        return {"status":"Toll Fee effective date should be future date."}
    else:
        if resp:
            return {'id':str(resp), "status": 'Toll Fee added successfully!!!'}
        else:
            return {"status":"Toll Fee records already present."}


@router.post("/edittollfee", tags=["Toll Fee"], include_in_schema=False)
def get_tollfee_data(request: schema.EditTollFeeSchema = Body(...)):
    company = request.dict().get('company')
    location = request.dict().get('location')
    tollid = request.dict().get('tollid')
    vehicletype = request.dict().get('vehicletype')
    tollfeedata = database.gettollfeedataforedit(company, location, tollid, vehicletype)
    return {'tollfeedata':tollfeedata}
    # return {"successful"}



@router.post("/savetollfee", tags=["Toll Fee"])
async def save_tollfee(data: schema.SaveTollFeeSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    if data.singlejourny==0 or data.retunjourney==0 or data.monthlypass==0 or data.retunjourney==0:
        return {"status":"Toll Fee rates can not be zero."}
    resp = database.savetollfeedata(data.dict())
    if resp == 0:
        return {"status": 'Toll Fee updated successfully!!!'}
    else:
        return {"status":"Failed"}





@router.post("/deletetollfee", tags=["Toll Fee"])
async def delete_tollfeevehicle(data: schema.DeletetollfeeSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    resp = database.deletetollfee(data.dict())
    if resp == -2:
        return {"status":"Failed"}
    else:
        if resp:
            return {'Number of records deleted':str(resp), "status": 'Toll Fee deleted successfully!!!!!!'}
        else:
            return {"status":"Toll Fee does not exist."}


@router.post('/update_tollfee', tags=["Toll Fee"],  include_in_schema=True)
async def upload_tollfee(file: UploadFile = File(...)):
   
    # for file in files:
    if file.content_type in ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
        file_location = os.path.join(data_dir, file.filename)
        
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        if file.content_type == 'text/csv':
            df = pd.read_csv(file_location, sep=',')
            tollfeedata = df.to_dict('records')
            database.updatetollfeedata(tollfeedata)

        if file.content_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            df = pd.read_excel(file_location)
            tollfeedata = df.to_dict('records')
            database.updatetollfeedata(tollfeedata)
    else:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail=f'File {file.filename} has unsupported extension type.')
    return {"Status": 'Toll fees data updated successfully!!!'}