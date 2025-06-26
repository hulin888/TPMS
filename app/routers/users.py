from fastapi import APIRouter, Depends, Body, HTTPException
from app.core.schemas import schema
from app.core.models.database import DATABASE
from app.admin.auth import AuthHandler
from app.admin import emailutil
import traceback
import uuid

router = APIRouter()
database = DATABASE()
auth_handler = AuthHandler()


@router.post('/adduser', status_code=201, tags=["User Management"])#, include_in_schema=False)
def add_user(auth_details: schema.AddUserSchema, username=Depends(auth_handler.auth_wrapper)):
    userdetails = database.check_user({"username":username})
    if userdetails.get('group') != "Super Admin" and auth_details.group == "Super Admin":
        raise HTTPException(status_code=403, detail="Operation not permitted")
    if auth_details.group == "Admin":
        auth_details.location = "All"
        auth_details.tollid = "All"
    if auth_details.group == "Manager":
        auth_details.tollid = "All"
    data = auth_details.dict()
    data['username'] = data['email']
    password = "abc12345"
    if database.check_user(data):
        raise HTTPException(status_code=400, detail='User with this email already present.')
    hashed_password = auth_handler.get_password_hash(password)
    data['password'] = hashed_password
    resp = database.add_user(data)
    if resp:
        database.insertuserlogs(username, "adduser")    
        return {'id':str(resp), "status": "User created successfully!!"}

@router.post('/updateuser', status_code=201, tags=["User Management"])#, include_in_schema=False)
def update_user(auth_details: schema.UpdateUserSchema, username=Depends(auth_handler.auth_wrapper)):
    data = auth_details.dict()
    data['username'] = data['email']
    if not database.check_user(data):
        raise HTTPException(status_code=400, detail='User with this email not present.')
    # hashed_password = auth_handler.get_password_hash(password)
    # data['password'] = hashed_password
    resp = database.updateuserdata(data)
    if resp:    
        database.insertuserlogs(username, "updateuser")
        return {"status": "User updated successfully!!"}

@router.post('/getuserdetails', tags=["User Management"])
# @router.post('/getusers', tags=["User Management"])

def get_users(request: schema.GetDataSchema, username=Depends(auth_handler.auth_wrapper)):
    data = request.dict()

    tollfeedata = database.getusersdata(data)
    return {'userdata':tollfeedata}

@router.post("/deleteuser", tags=["User Management"])
async def delete_user(data: schema.DeleteUserSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    resp = database.deleteuser(data.dict())
    if resp == -2:
        return {"status":"Failed"}
    else:
        if resp:
            database.insertuserlogs(username, "deleteuser")
            return {'Number of records deleted':str(resp), "status": 'User deleted successfully!!!!!!'}
        else:
            return {"status":"User does not exist."}

@router.post("/resetpassword", tags=["User Management"])
async def resetpassword(requetdata: schema.ResetUserSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    password = "abc12345"
    hashed_password = auth_handler.get_password_hash(password)
    resp = database.reset_password(requetdata.dict(), hashed_password)
    # resp = database.add_user(data)
    if resp == -2:
        return {"status":"Failed"}
    else:
        if resp:
            database.insertuserlogs(username, "resetpassword")
            return {"status": "Password reset successfully!!"}
        else:
            return {"status":"User does not exist."}  

@router.post("/changepassword", tags=["User Management"])
async def changepassword(requetdata: schema.ChangePasswordSchema = Body(...), username=Depends(auth_handler.auth_wrapper)):
    # password = "abc12345"
    if requetdata.new_password != requetdata.confirm_password:
        raise HTTPException(status_code=404, detail="Password doesn't match.")
    hashed_password = auth_handler.get_password_hash(requetdata.new_password)
    resp = database.change_password(requetdata.dict(), hashed_password)
    # resp = database.add_user(data)
    if resp == -2:
        return {"status":"Failed"}
    else:
        if resp:
            database.insertuserlogs(username, "changepassword")
            return {"status": "Password changed successfully!!"}
        else:
            return {"status":"User does not exist."} 
 
@router.post('/register', status_code=201, tags=["User Management"])#, include_in_schema=False)
def register(auth_details: schema.RegUserSchema):
    data = auth_details.dict()
    data['username'] = data['email']
    if database.check_user(data):
        raise HTTPException(status_code=400, detail='User with this email already present.')
    hashed_password = auth_handler.get_password_hash(auth_details.password)
    data['password'] = hashed_password
    resp = database.add_user(data)
    if resp:    
        return {"status": "User created successfully!!"}
    

@router.post('/login', tags=["Users"])#, include_in_schema=False)
def login(auth_details: schema.AuthDetails):
    user = None
    user = database.check_user(auth_details.dict())
    
    if (user is None) or (not auth_handler.verify_password(auth_details.password, user['password'])):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(user['username'])
    user.pop('password')
    # user.pop('_id')
    database.insertuserlogs(auth_details.username, "login")
    return { 'token': token, 'userprofile': user }

@router.post('/getprofile', tags=["My Profile"])#, include_in_schema=False)
def login(auth_details: schema.AuthDetails):
    user = None
    user = database.check_user(auth_details.dict())
    
    if (user is None) or (not auth_handler.verify_password(auth_details.password, user['password'])):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    # token = auth_handler.encode_token(user['username'])
    user.pop('password')
    user.pop('_id')
    return { 'userprofile': user }

@router.get('/getgroups' , tags=["User Management"])
def get_groups(username=Depends(auth_handler.auth_wrapper)):
    vehicletypes = database.getgroupsdata()
    return {'groups':vehicletypes}

@router.get('/protected' , include_in_schema=False)
def protected(username=Depends(auth_handler.auth_wrapper)):
    return { 'name': username }