# hand-solo-quasar
Trilateration 

this code use trilateration for get tx location using 3 (or more) reference points and lineal distance to each point from tx '.

![trilateriation](https://www.alanzucconi.com/wp-content/uploads/2017/03/Trilateration3.png)

the aim is get the intersection points betweem the circles with R = Distance
after we need to calculate the distances for each intersection points to others, and the first minumun distance is the converge point -tx location-, 
this method is called [Geometric Median](https://en.wikipedia.org/wiki/Geometric_median)

Note: in the real life the system using more complex for solve location like GPS, other systems using [multiration](https://www.wikiwand.com/en/True-range_multilateration) for get the location with the minumun error. 

*real time app [here](https://quasar-iwmtxlug5a-uc.a.run.app)*

## Getting started 

### requirements
 - source code `git clone https://github.com/Cubillosxy/hand-solo-quasar.git`
 - docker 
 

### run server
 - `docker build -t quasar .`
 - `docker run -d --name quasar_latest -p 8080:8080 quasar`   _or_   `docker run -p 8080:8080 quasar`


## Testing

run test case with pytest 

 - `pytest`
 - run on the build image `docker container run quasar pytest`
 - on image running `docker exec -it quasar_latest pytest`

## API  docs

thanksn to [swagger](https://swagger.io/) and [redoc](https://github.com/Redocly/redoc) integration you have a interative docs for test your endpoints.

- go to  [/docs](/docs) or [/redoc](/redoc)


# Code
This Api has been performed with [FAST API](https://fastapi.tiangolo.com/) 



Arquitecture - Service Layer 

Deployed with Google Cloud Platform


## Deploying ...
The last version of this code is runing on time [here](https://quasar-iwmtxlug5a-uc.a.run.app)

#referenes 
 - https://github.com/jurasofish/multilateration