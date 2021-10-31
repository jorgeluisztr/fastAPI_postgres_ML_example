# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pickle
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import schema
from models import Passenger
from models import Passenger as ModelPassenger
from schema import Passenger as SchemaPassenger
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

#from typing import List

load_dotenv(".env")

app = FastAPI()

engine = os.environ["DATABASE_URL"]
engine = create_engine(engine)
Session = sessionmaker(bind=engine)
db = Session()
#app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])

# Define object we classify
def ageLevels(person):
    """

    :param person: PersonInfo class
    :return: the numerical class of age for a person
    """
    if person.Age <= 16:
        return 0
    elif person.Age > 16 and person.Age <= 32:
        return 1
    elif person.Age > 32 and person.Age < 48:
        return 2
    elif person.Age > 48 and person.Age < 64:
        return 3
    else:
        return 4

def isAlone(person):
    """

    :param person: PersonInfo class
    :return: dummy varibale about if this person travel alone
    """
    familysize = person.Sibsp + person.Parch + 1
    if familysize == 1:
        return 1
    else:
        return 0

def title(name):
    """

    :param name: name of a person str
    :return: the corresponding numerical title of a person
    """
    for t in ['Lady', 'Countess', 'Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona']:
        if t in name:
            return 5

    if 'Mlle' in name or 'Miss' in name or 'Ms' in name:
        return 2
    elif 'Mme' in name or 'Mrs' in name:
        return 3
    elif 'Mr' in name:
        return 1
    elif 'Master' in name:
        return 4
    else:
        return 0

def fareLevels(person):
    """

    :param person: PersonInfo class
    :return: a numerical fare level
    """
    if person.Fare <= 7.91:
        return 0
    elif person.Fare > 7.91 and person.Fare <= 14.454:
        return 1
    elif person.Fare > 7.91 and person.Fare <= 31:
        return 2
    else:
        return 3

def embarkedCategorical(person):
    """

    :param person: PersonInfo class
    :return: numerical value for the port of embarkation
    """
    embarked = {'S': 0, 'C': 1, 'Q': 2}
    return (embarked[person.Embarked])

class passengerInfo(BaseModel):
    pid: int
    Pclass: int
    Name: str
    Sex: str
    Age: float
    Sibsp: int
    Parch: int
    Ticket: str
    Fare: float
    Cabin: str
    Embarked: str

class SurvivePredictor:
    """
    The clas to predict if a person on the titanic would survive
    """

    def __init__(self):

        self.model = pickle.load(open("logistic_regression.pickle", "rb"))

    def predict(self, person: passengerInfo):
        """

        :param person: PersonInfo class
        :return: the output of a logistic regression if a passenger would survive or not
        """
        # make sure that here the order is the same as in the model training
        print("person:", person)

        x = np.array([person.Pclass,
                      1 if person.Sex == "female" else 0,
                      ageLevels(person),
                      fareLevels(person),
                      embarkedCategorical(person),
                      title(person.Name),
                      isAlone(person),
                      person.Age*person.Pclass])

        x = x.reshape(1, -1)
        y = self.model.predict(x)

        return y

app = FastAPI()
predictor = SurvivePredictor()

# Server Definition
@app.get("/")
def root():
    return {"GoTo": "/docs"}

@app.post("/add-passenger/", response_model=passengerInfo)
def add_passenger(passenger: passengerInfo):
    """

    **param** \n passenger: PersonInfo class, \n
    **return** \n  store in a table if the passenger survive or not
    """
    passenger_db = ModelPassenger(pid=passenger.pid, pclass=passenger.Pclass, name=passenger.Name,
                                  sex=passenger.Sex, age=passenger.Age, sibsp=passenger.Sibsp,
                                  parch=passenger.Parch, ticket=passenger.Ticket, fare=passenger.Fare,
                                  cabin=passenger.Cabin, embarked=passenger.Embarked,
                                  survived=int(predictor.predict(passenger)[0]))
    db.add(passenger_db)
    try:
        db.commit()
    except:
        db.delete()
        raise "Rollback Error"

    db.query(passenger_db).all()
    return passenger_db