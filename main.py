from fastapi import FastAPI, Response, status

from models import (
    SatellitesList, TxResponse
)
from utils import Trilateration

app = FastAPI()


@app.post('/topsecret')
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
