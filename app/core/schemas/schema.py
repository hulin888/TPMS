from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from fastapi import Form
from typing import List, Optional


class Jobid(BaseModel):
    job_id: str

class filepath(BaseModel):
    filepath: str

class Queryparams(BaseModel):
    licence_plate: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_subtype: Optional[str] = None
    datefrom: Optional[datetime] = None
    dateto: Optional[datetime] = None

class TransactionTableSchema(BaseModel):
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    laneno: str = Field(...)
   

    class Config:
        schema_extra = {
            "example": {
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "laneno": "1"
            }
        }

class AddSetupSchema(BaseModel):
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    laneno: str = Field(...)
    inout: str = Field(...)
    cctvlink: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "laneno": "2",
                "inout": "in",
                "cctvlink": "rtsp://admin:admin@192.168.0.10:8554/CH001.sdp"
            }
        }

class SaveSetupSchema(BaseModel):
    id: str = Field(...)
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    laneno: str = Field(...)
    inout: str = Field(...)
    cctvlink: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "id": "61c193996023b44c1e53cd66", 
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "laneno": "2",
                "inout": "in",
                "cctvlink": "rtsp://admin:admin@192.168.0.10:8554/CH001.sdp"
            }
        }

class DeletesetupSchema(BaseModel):
    id: str = Field(...)

    
    class Config:
        schema_extra = {
            "example": {
                "id": "61c1a73793f4dd3da9ad4e3c",

            }
        }

class GetDataSchema(BaseModel):
    location: str
    tollno: str

class GetDataSchema(BaseModel):
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10"
            }
        }
    
class DashbordSchema_new(BaseModel):
    company: str = Field(...)
    location: List[str] = Field(...)
    tollid: List[str] = Field(...)
    laneno: Optional[List[str]] = None
    vehicleno: Optional[str] = None
    vehicletype: Optional[str] = None
    vehiclesubtype: Optional[str] = None
    datefrom: Optional[datetime] = None
    dateto: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "company": "ABC Toll Plaza",
                "location": ["Nagpur"],
                "tollid": ["10"],
                "laneno": [""],
                "vehicleno": "",
                "vehicletype": "",
                "vehiclesubtype": "",
                "datefrom": datetime(2021, 8, 1, 00, 00, 00),
                "dateto":  datetime(2021, 9, 1, 00, 00, 00),
            }
        }

class DashbordSchema(BaseModel):
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    laneno: Optional[str] = None
    vehicleno: Optional[str] = None
    vehicletype: Optional[str] = None
    vehiclesubtype: Optional[str] = None
    datefrom: Optional[datetime] = None
    dateto: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "laneno": "",
                "vehicleno": "",
                "vehicletype": "",
                "vehiclesubtype": "",
                "datefrom": datetime(2021, 8, 1, 00, 00, 00),
                "dateto":  datetime(2021, 9, 1, 00, 00, 00),
            }
        }
class TollFeeSchema(BaseModel):
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    vehicletype: str = Field(...)
    vehiclesubtype: str = Field(...)
    singlejourny: int = Field(...)
    retunjourney: int = Field(...)
    monthlypass: int = Field(...)
    commercialvehicleregisteredwithinthedistrictofplaza: int = Field(...)
    effectivedate: datetime = Field(...)
    # tilldate: datetime = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "vehicletype": "Car/Jeep/Van",
                "vehiclesubtype":"Car/Jeep/Van",
                "singlejourny":110,
                "retunjourney":160,
                "monthlypass":3450,
                "commercialvehicleregisteredwithinthedistrictofplaza":55,
                "effectivedate":datetime(2021, 12, 21, 00, 00, 00),
                # "tilldate":datetime(9999, 1, 1, 00, 00, 00)

            }
        }

class EditTollFeeSchema(BaseModel):
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    vehicletype: str = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "vehicletype": "Car/Jeep/Van"
            }
        }

class SaveTollFeeSchema(BaseModel):
    id: str = Field(...)
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    vehicletype: str = Field(...)
    singlejourny: int = Field(...)
    retunjourney: int = Field(...)
    monthlypass: int = Field(...)
    commercialvehicleregisteredwithinthedistrictofplaza: str = Field(...)
    effectivedate: datetime = Field(...)
    tilldate: datetime = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "id": "61c193996023b44c1e53cd66",
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "vehicletype": "Car/Jeep/Van",
                "singlejourny":110,
                "retunjourney":160,
                "monthlypass":3450,
                "commercialvehicleregisteredwithinthedistrictofplaza":55,
                "effectivedate":datetime(2021, 12, 21, 00, 00, 00),
                "tilldate":datetime(9999, 1, 1, 00, 00, 00)

            }
        }

class DeletetollfeeSchema(BaseModel):
    id: str = Field(...)

    
    class Config:
        schema_extra = {
            "example": {
                "id": "61c1a73793f4dd3da9ad4e3c",

            }
        }

class ExemptedvehicleSchema(BaseModel):
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    vehicleno: str = Field(...)
    vehicletype: str = Field(...)
    vehiclesubtype: str = Field(...)
    exemptiontag: str = Field(...)
    
    class Config:
        schema_extra = {
            "example": {
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "vehicleno":"MH 12 5624",
                "vehicletype": "car",
                "vehiclesubtype":"car",
                "exemptiontag":"Y",
            }
        }

class EditExemptedvehicleSchema(BaseModel):
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    vehicleno: str = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "vehicleno": "MH 12 5624"
            }
        }

class SaveExemptedvehicleSchema(BaseModel):
    id: str = Field(...)
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    vehicleno: str = Field(...)
    vehicletype: str = Field(...)
    vehiclesubtype: str = Field(...)
    exemptiontag: str = Field(...)
    
    class Config:
        schema_extra = {
            "example": {
                "id":"61c1565642b8b436a8235595",
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "vehicleno":"MH 12 5624",
                "vehicletype": "car",
                "vehiclesubtype":"car",
                "exemptiontag":"Y",
            }
        }

class DeleteexemptedvehicleSchema(BaseModel):
    id: str = Field(...)
   
    class Config:
        schema_extra = {
            "example": {
                "id": "61c1a73793f4dd3da9ad4e3c",

            }
        }
class UploadExemptedVehiclesData(BaseModel):
    company: str = Form(...)
    location: str = Form(...)
    tollid: str = Form(...)

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "company": "ABC Toll Plaza",
    #             "location": "Nagpur",
    #             "tollid": "10",
    #         }
    #     }

class MonthlyPassSchema(BaseModel):
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    vehicleno: str = Field(...)
    vehicletype: str = Field(...)
    vehiclesubtype: str = Field(...)
    startdate: datetime = Field(...)
    enddate: datetime = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "vehicleno": "MH 12 5624",
                "vehicletype": "car",
                "vehiclesubtype":"car",
                "startdate":datetime(2021, 12, 21, 00, 00, 00),
                "enddate":datetime(2021, 1, 11, 00, 00, 00)

            }
        }

class EditMonthlyPassSchema(BaseModel):
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    vehicleno: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "vehicleno": "MH 12 5624",
            }
        }

class SaveMonthlyPassSchema(BaseModel):
    id: str = Field(...)
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    vehicleno: str = Field(...)
    vehicletype: str = Field(...)
    vehiclesubtype: str = Field(...)
    startdate: datetime = Field(...)
    enddate: datetime = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "id": "61c1a73793f4dd3da9ad4e3c",
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "vehicleno": "MH 12 5624",
                "vehicletype": "car",
                "vehiclesubtype":"car",
                "startdate":datetime(2021, 12, 21, 00, 00, 00),
                "enddate":datetime(2021, 1, 11, 00, 00, 00)

            }
        }

class DeletemonthlypassvehicleSchema(BaseModel):
    id: str = Field(...)

    
    class Config:
        schema_extra = {
            "example": {
                "id": "61c1a73793f4dd3da9ad4e3c",

            }
        }

class CvrDtpSchema(BaseModel):
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    vehicleno: str = Field(...)
    vehicletype: str = Field(...)
    vehiclesubtype: str = Field(...)
    startdate: datetime = Field(...)
    
    class Config:
        schema_extra = {
            "example": {
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "vehicleno": "MH12TZ5624",
                "vehicletype": "car",
                "vehiclesubtype":"car",
                "startdate":datetime(2021, 12, 21, 00, 00, 00),

            }
        }

class SaveCvrDtpSchema(BaseModel):
    id: str = Field(...)
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    vehicleno: str = Field(...)
    vehicletype: str = Field(...)
    vehiclesubtype: str = Field(...)
    startdate: datetime = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "id": "61c1a73793f4dd3da9ad4e3c",
                "company": "ABC Toll Plaza",
                "location": "Nagpur",
                "tollid": "10",
                "vehicleno": "MH 12 5624",
                "vehicletype": "car",
                "vehiclesubtype":"car",
                "startdate":datetime(2021, 12, 21, 00, 00, 00),

            }
        }

class DeletecvrdtpvehicleSchema(BaseModel):
    id: str = Field(...)
    

    class Config:
        schema_extra = {
            "example": {
                "id": "61c1a73793f4dd3da9ad4e3c",

            }
        }

class RegUserSchema(BaseModel):
    email: EmailStr = Field(...)
    company: str = Field(...)
    group: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    activestatus: str = Field(...)
    password: str = Field(...)

class AddUserSchema(BaseModel):
    company: str = Field(...)
    group: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    activestatus: str = Field(...)
    email: EmailStr = Field(...)

class UpdateUserSchema(BaseModel):
    id: str = Field(...)
    company: str = Field(...)
    group: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    activestatus: str = Field(...)
    email: EmailStr = Field(...)

class DeleteUserSchema(BaseModel):
    id: str = Field(...)

    
    class Config:
        schema_extra = {
            "example": {
                "id": "61c1a73793f4dd3da9ad4e3c",

            }
        }

class ResetUserSchema(BaseModel):
    id: str = Field(...)
    # company: str = Field(...)
    # location: str = Field(...)
    # tollid: str = Field(...)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "61c1a73793f4dd3da9ad4e3c",
                # "company": "ABC Toll Plaza",
                # "location": "Nagpur",
                # "tollid": "10"
            }
        }
class ChangePasswordSchema(BaseModel):
    company: str = Field(...)
    location: str = Field(...)
    tollid: str = Field(...)
    email: EmailStr = Field(...)
    new_password: str
    confirm_password: str
class AuthDetails(BaseModel):
    username: str
    password: str


class ForgotPassword(BaseModel):
    username: EmailStr = Field(...)

class ResetPassword(BaseModel):
    reset_password_token : str
    new_password: str
    confirm_password: str

class Help(BaseModel):
    company: str
    location: str
    tollid: str
    query : str
    details: str
