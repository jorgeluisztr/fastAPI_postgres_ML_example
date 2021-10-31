from pydantic import BaseModel


class Passenger(BaseModel):
    pid: int
    pclass: int
    name: str
    sex: str
    age: float
    sibsp: int
    parch: int
    ticket: str
    fare: float
    cabin: str
    embarked: str
    survived: float

    class Config:
        orm_mode = True



