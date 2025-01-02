from pydantic import BaseModel,EmailStr,field_validator,Field,Optional

class User(BaseModel):
    id: str
    email: EmailStr
    password: str
    designation: str= "user"|"toll"|"police"
    name: str


class Transaction(BaseModel):
    id: str
    timestamp: str
    tagId: str
    amount: int = Field(gt=0)
    type: str="debit"|"credit"
    description: str ="Recharge"|"Challan Payment"|"Toll Plaza Passage" |"Forced Challan Payment"

class Challan(BaseModel):
    id: str
    vehicleId: str
    amount: int = Field(gt=0)
    location: str
    description: str
    date: str
    due_time: int
    status: str="settled"|"unsettled"
    settlement_date: Optional[str] = Field(default="")

class Fastag(BaseModel):
    id: str
    balance: int = Field(gt=0)
    status: str="valid"|"invalid"
    email: EmailStr
    vehicleId: str

class Vehicle(BaseModel):
    id: str
    email: EmailStr
    tagId: Optional[str] = Field(default="")