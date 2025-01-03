from pydantic import BaseModel,EmailStr,field_validator,Field
from utils.password import check_password_strength,PASSWORD_CONSTRAINT
import time

class User(BaseModel):
    email: EmailStr
    password: str
    designation: str
    name: str

    @field_validator("password")
    def validate_pass_word(cls, value):
        if check_password_strength(value):
            return value
        else:
            raise ValueError(
                f"Invalid password....\n{PASSWORD_CONSTRAINT}"
            )
    
    @field_validator("designation")
    def validate_designation(cls, value):
        if value=="police" or value=="toll" or value=="user":
            return value
        else:
            raise ValueError(
                f"Invalid designation"
            )

class Transaction(BaseModel):
    timestamp: str
    tag_id: str
    amount: int = Field(gt=0)
    type: str
    description:str
    location:str

    @field_validator("type")
    def validate_transaction_type(cls, value):
        if value=="credit" or value=="debit":
            return value
        else:
            raise ValueError(
                f"Invalid type of transaction"
            )
        
    @field_validator("description")
    def validate_description(cls, value):
        if value=="recharge" or value == "challan payment" or value=="toll plaza payment" or value=="forced overdue challan payment":
            return value
        else:
            raise ValueError(
                f"Invalid type of transaction"
            )


class Challan(BaseModel):
    vehicle_id: str
    amount: int = Field(gt=0)
    location: str
    description: str
    date:int= Field(default=time.time())
    due_time:int=Field(default= time.time()+60*60*24*90)
    status: str = Field(default="unsettled")
    settlement_date: str=Field(default="")

    @field_validator("status")
    def validate_status(cls,value):
        if value == "settled" or value =="unsettled":
            return value
        else:
            return ValueError("Invalid Status")

class Fastag(BaseModel):
    id: str
    balance: int = Field(gt=-1)
    status : str
    email: EmailStr
    vehicle_id: str

    @field_validator("status")
    def validate_designation(cls, value):
        if value=="valid" or value =="invalid":
            return value
        else:
            raise ValueError(
                f"Invalid status"
            )

    @field_validator("balance")
    def validate_balance(cls,value):
        if value<0 or type(value)!=int:
            raise ValueError("Invalid balance")
        else:
            return value

class Vehicle(BaseModel):
    id: str
    email: EmailStr
    tag_id: str

class LoginModel(BaseModel):
    email:EmailStr
    password:str

    @field_validator("password")
    def validate_pass_word(cls, value):
        if check_password_strength(value):
            return value
        else:
            raise ValueError(
                f"Invalid password....\n{PASSWORD_CONSTRAINT}"
            )