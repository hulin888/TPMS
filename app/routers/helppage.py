from fastapi import APIRouter, Depends, Body
from app.core.schemas import schema
from app.core.models.database import DATABASE
from app.admin import emailutil
from app.admin.auth import AuthHandler
import traceback

router = APIRouter()
database = DATABASE()
auth_handler = AuthHandler()


@router.post('/help', tags=["Users"])
async def contact_us(request: schema.Help, username=Depends(auth_handler.auth_wrapper)):
    recipient = ['sdpatil123456@gmail.com']
    message = f'''
    <!DOCTYPE html>
    <html>
    <body>
        <p> Hi Support Team,</p>
        <p> We have received a help request from </p>
        <h3>Company: {request.company}, Location: {request.location}, TollID: {request.tollid}.</h3>
        <P> <b>The details are: </b></p>
        <p> {request.details}</p>
    </body>
    </html>
    '''
    await emailutil.send_email(request.query, recipient, message)
    return {"status":" Your query has been registered successfully."}