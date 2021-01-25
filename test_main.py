from fastapi.testclient import TestClient
from main import app
from models import Satellite
from utils import Trilateration
import random



client = TestClient(app)

tx_location = (random.randint(-500, 500), random.randint(-500, 500))


def test_not_enought_data():
    s1 = Satellite(name='test', distance=1, message=['test'])
    data = {
        "satellites": [s1.dict()]
    }
    response = client.post("/topsecret", json=data)
    assert response.status_code == 404
    assert response.json() == {
        "error": Trilateration.ERROR_NOT_ENOUGH_DATA
    }



def test_invalid_data():
    s1 = Satellite(name='test', distance=1, message=['test'])
    data = {
        "satellites": [s1.dict() for i in range(3)]
    }
    response = client.post("/topsecret", json=data)
    assert response.status_code == 404
    assert response.json() == {
        "error": Trilateration.ERROR_INVALID_DATA_LENGHT
    }


def test_unable_to_get_msg():


    satellites = [
        {
            'distance': Trilateration.distance_x_y(tx_location, [i['value']])['value'],
            'message': ['', 'imposible', '', ''],
            'name': i['name']

        } for i in Trilateration.get_satellites_list()
    ]

    data = {
        "satellites": satellites
    }
    response = client.post("/topsecret", json=data)
    assert response.status_code == 404
    assert response.json() == {
        "error": Trilateration.ERROR_UNABLE_GET_MESSAGE
    }




