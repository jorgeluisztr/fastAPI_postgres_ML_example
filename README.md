## fastAPI_postgres_ML_example
This is a very simple api to store results of a machine learning model to a table


The main idea from this repo is to show how to use fastapi, postgres and docker compose to create an api with a trained model of ML to consume its results. 

One great material to understand how to use fastAPI is [this video](https://www.youtube.com/watch?v=1zMQBe0l1bM&t=3476s).

**The logistic regression model used in this app (as a pickle) was obtained from** [here](https://www.kaggle.com/startupsci/titanic-data-science-solutions).

**Warning**


Please check the ip adress of your postgres container using
  
  ```docker inspect your-container-id | grep IPAdress```
  
and then change it from docker-compose
