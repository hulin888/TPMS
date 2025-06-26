from fastapi import APIRouter, Depends, Body
from app.core.schemas import schema
from app.core.models.database import DATABASE
from app.admin.auth import AuthHandler
import traceback
import re

router = APIRouter()
database = DATABASE()
auth_handler = AuthHandler()

@router.post('/getcvrdtpvehicles', tags=["CVR within DTP"])
def get_cvrdtpvehicles_data(request: schema.GetDataSchema, username=Depends(auth_handler.auth_wrapper)):
    company = request.dict().get('company')
    location = request.dict().get('location')
    tollid = request.dict().get('tollid')
    cvrdtpvehicles = database.getcvrdtpvehicledata(company, location, tollid)
    return {'cvrdtpvehicles':cvrdtpvehicles}


@router.post("/addcvrdtpvehicle", tags=["CVR within DTP"])
async def add_addcvrdtpvehicle(data: schema.CvrDtpSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    if re.match('^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{3,4}$', data.vehicleno.replace(" ", '')):
        resp = database.addcvrdtpvehicle(data.dict())
        if resp == -2:
            return {"status":"Failed"}
        else:
            if resp:
                return {'id':str(resp), "status": 'Commercial Vehicle within District Toll Plaza added successfully!!!!!!'}
            else:
                return {"status":"Commercial Vehicle within District Toll Plaza records already present."}
    else:
        return {"status":"Enter correct vehicle number!"}


@router.post("/savecvrdtpvehicle", tags=["CVR within DTP"])
async def save_cvrdtpvehicle(data: schema.SaveCvrDtpSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    if re.match('^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{3,4}$', data.vehicleno):
        resp = database.savecvrdtpvehicle(data.dict())
        if resp == 0:
            return {"status": 'Commercial Vehicle within District Toll Plaza data updated successfully!!!'}
        else:
            return {"status":"Failed"}
    else:
        return {"status":"Enter correct vehicle number!"}



@router.post("/deletecvrdtpvehicle", tags=["CVR within DTP"])
async def delete_cvrdtpvehicle(data: schema.DeletecvrdtpvehicleSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    resp = database.deletecvrdtpvehicle(data.dict())
    if resp == -2:
        return {"status":"Failed"}
    else:
        if resp:
            return {'Number of records deleted':str(resp), "status": 'Commercial Vehicle within District Toll Plaza deleted successfully!!!!!!'}
        else:
            return {"status":"Commercial Vehicle within District Toll Plaza does not exist."}