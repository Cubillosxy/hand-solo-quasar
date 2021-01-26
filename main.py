from fastapi import (
    FastAPI,
    Response,
    status,
    Depends,
    Request, 
    Cookie
)

from fastapi.responses import HTMLResponse
import jwt
import json
from typing import Optional

from models import (
    SatellitesList, 
    TxResponse,
    SatelliteBase
)
from markdown import markdown

from utils import Trilateration
from utils import TOP_SECRECT, SECRECT_KEY, TOP_SECRECT_SPLIT, MIN_DATA_LENGTH

app = FastAPI()
satellites_names = Trilateration.get_satellites_names(Trilateration.get_satellites_list())


@app.get("/", response_class=HTMLResponse)
def home():
    readme = ''
    with open('README.md', 'r+') as f:
        readme = f.read()

    return markdown(readme)

    

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
def topsecret_split(satellite_name: str, satellite_base: SatelliteBase, response: Response, data: Optional[str]  = Cookie(None)):

    def _return_error(error):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error' : error}

    if satellite_name.lower() not in satellites_names:
        return _return_error(Trilateration.ERROR_INVALID_DATA)

    if data:
        if isinstance(data, str):
            data = json.loads(data)

        data[satellite_name] = satellite_base.dict()
        response.set_cookie('data', data)

    else:
        response.set_cookie('data', {satellite_name: satellite_base.dict()})

    response.status_code = status.HTTP_201_CREATED
    return {}


@app.get(f'{TOP_SECRECT}reset-data/')
def topsecret_reset_data(response: Response):
    response.set_cookie('data', {})
    return {'reset': 'ok'}

@app.get(TOP_SECRECT_SPLIT)
def topsecret_split_get(response: Response, data: Optional[str] = Cookie(None)):
    if data:
        if isinstance(data, str):
            data = json.loads(data)

        if len(data.keys()) >= MIN_DATA_LENGTH:
            trilateration = Trilateration(input_data=data)
            error = trilateration.prepare_standarized()

            if not error:
                message = trilateration.get_message()
                x_y = trilateration.get_location()
                if message is not None and x_y is not None:
                    position = {
                        'x': x_y[0], 'y': x_y[1]
                    }

                    response = TxResponse(position=position, message=message)
                    return response.dict()

    return {'error': Trilateration.ERROR_NOT_ENOUGH_DATA}
    