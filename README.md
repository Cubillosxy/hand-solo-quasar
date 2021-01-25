# hand-solo-quasar
Trilateration problem 




## Getting started 

### requirements

 - docker 
 - # teste on linux 

### run server
 - `docker build -t quasar .`
 - `docker run -d --name quasar_latest -p 80:80 quasar` or `docker run -p 80:80 quasar`


## testing

run test case with pytest 

 - `pytest`
 - run on the build image `docker container run quasar pytest`
 - on image running `docker exec -it quasar_latest pytest`

##  docs

thansks to swagger integration you have a interative docs for test your endpoints
 - go to `/docs`
