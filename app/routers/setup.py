from fastapi import APIRouter, Depends, Body
from app.core.schemas import schema
from app.core.models.database_setup import DATABASE_SETUP
from app.admin.auth import AuthHandler
from app import tasks
import traceback

router = APIRouter()
database = DATABASE_SETUP()
auth_handler = AuthHandler()


@router.post('/addsetup', tags=["Setup"])
def setup_process(data: schema.AddSetupSchema, username=Depends(auth_handler.auth_wrapper)):
    try:
        # process_video(data)
        resp = database.setup_data(data.dict())
        print(resp)
        if resp == -2:
            return {"status":"Failed"}
        else:
            if resp:
                tasks.docextractor.apply_async([data.company, data.location, data.tollid, data.laneno, data.inout, data.cctvlink])
                tasks.datatoserver.apply_async()
                return {'id':str(resp), "status": 'Camera Setup done successfully!!!'}
            else:
                return {"status":"Camera Setup already done for this lane."}
    except:
        print(traceback.print_exc())
        return {"status":"Failed"}



@router.post('/savesetup', tags=["Setup"])
def savesetup(data: schema.SaveSetupSchema, username=Depends(auth_handler.auth_wrapper)):
    try:
        # process_video(data)
        resp = database.savesetupdata(data.dict())
        if resp == 0:
            tasks.docextractor.apply_async([data.company, data.location, data.tollid, data.laneno, data.inout, data.cctvlink])
            return {"status": 'Setup data updated successfully!!!'}
        else:
            return {"status":"Failed"}
    except:
        print(traceback.print_exc())
        return {"status":"Failed"}

@router.post('/getsetupdetails' , tags=["Setup"])
def get_setupdetails(request: schema.GetDataSchema, username=Depends(auth_handler.auth_wrapper)):
    company = request.dict().get('company')
    location = request.dict().get('location')
    tollid = request.dict().get('tollid')
    setupdetails = database.getsetupdetails(company, location, tollid)
    return {'setupdetails':setupdetails}

@router.post('/getcamerastatus' , tags=["Setup"])
def get_camerastatus(request: schema.GetDataSchema, username=Depends(auth_handler.auth_wrapper)):
    company = request.dict().get('company')
    location = request.dict().get('location')
    tollid = request.dict().get('tollid')
    active, inactive = database.getcamerastatusdetails(company, location, tollid)
    return {'activecamearas':active, 'inactivecamearas':inactive}

@router.post("/deletesetup", tags=["Setup"])
async def delete_setup(data: schema.DeletesetupSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    resp = database.deletesetup(data.dict())
    if resp == -2:
        return {"status":"Failed"}
    else:
        if resp:
            return {'Number of records deleted':str(resp), "status": 'Setup deleted successfully!!!!!!'}
        else:
            return {"status":"Setup does not exist."}