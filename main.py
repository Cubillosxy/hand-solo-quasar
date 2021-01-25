from fastapi import FastAPI, Response, status, Depends
from fastapi.security import APIKeyCookie
import jwt

from models import (
    SatellitesList, 
    TxResponse,
    SatelliteBase
)
from utils import Trilateration
from utils import TOP_SECRECT, SECRECT_KEY, TOP_SECRECT_SPLIT

app = FastAPI()



cookie_sec = APIKeyCookie(name="session")
satellites_names = Trilateration.get_satellites_names(Trilateration.get_satellites_list())


def get_current_session(session: str = Depends(cookie_sec)):
    try:
        payload = jwt.decode(session, SECRECT_KEY)
        return payload
    except ValueError:
        pass

@app.post(TOP_SECRECT)
def topsecret(data: SatellitesList, response: Response):
    '''
    calculate position according 3 points (SATELITES) using trilateration method 
    -> return position and decode message

    '''

    def _return_error(error):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error' : error}

    satellites = data.dict()['satellites']
    
    trilateration = Trilateration(satellites)
    error = trilateration.prepare()

    if error:
        return _return_error(error)
    
    message = trilateration.get_message()
    x_y = trilateration.get_location()

    if message is None:
        return _return_error(trilateration.ERROR_UNABLE_GET_MESSAGE)

    if x_y is None:
        return _return_error(trilateration.ERROR_UNABLE_GET_LOCATION)

    position = {
        'x': x_y[0], 'y': x_y[1]
    }

    response = TxResponse(position=position, message=message)

    return response.dict()


@app.post(TOP_SECRECT_SPLIT+'{satellite_name}')
def topsecret_split(satellite_name: str, satellite_base: SatelliteBase, response: Response, payload: str = Depends(get_current_session)):

    def _return_error(error):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error' : error}

    if satellite_name.lower() not in satellites_names:
        return _return_error(Trilateration.ERROR_INVALID_DATA)

    token = jwt.encode({"sub": username}, secret_key)

    return {'hola': 23}


@app.get(TOP_SECRECT_SPLIT)
async def topsecret_split_get( response: Response):
    return {'hola': 'get'}
    