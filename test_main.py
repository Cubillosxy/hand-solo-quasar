from fastapi.testclient import TestClient
from main import app
from models import Satellite, TxResponse
from utils import Trilateration
import random


client = TestClient(app)
xo, yo = random.randint(-500, 500), random.randint(-500, 500)
tx_location = (xo, yo)


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



def test_repeat_msg():

    good_msg = ['test', 'my', 'app', 'ok']
    satellites = [
        {
            'distance': Trilateration.distance_x_y(tx_location, [i['value']])['value'],
            'message': good_msg,
            'name': i['name']

        } for i in Trilateration.get_satellites_list()
    ]

    data = {
        "satellites": satellites
    }
    response = client.post("/topsecret", json=data)
    assert response.status_code == 200

    # we know tha position is close to the real position

    assert response.json() == {
        'message' :' '.join(good_msg),
        'position': {'x': float(xo), 'y': float(yo)}
    }


def test_decode_msg():
    good_1 =  ['test', 'my', 'app', 'ok']
    mgs1 = [
        ['test', '', 'app', 'ok'],
        ['', '', 'app', 'ok'],
        ['', 'my', 'app', ''],
    ]

    mgs2 = [
        ['test', '', 'app', 'ok'],
        ['', '', 'app', 'ok'],
        ['', 'my', '', ''],
    ]

    good_3 = ['my', 'app', 'ok']
    mg3 = [
        ['', 'my', '', 'ok'],
        ['my', 'app', ''],
        ['', 'my', '', 'ok'],
    ]

    satellites = [
        {
            'distance': Trilateration.distance_x_y(tx_location, [i['value']])['value'],
            'name': i['name']

        } for i in Trilateration.get_satellites_list()
    ]


    _custom = []

    for i, j in enumerate(satellites):
        _aux = dict(j)
        _aux['message'] = mgs1[i]
        _custom.append(_aux)



    data = {
        "satellites": _custom
    }
    print('data', data)
    response = client.post("/topsecret", json=data)
    print(response.json())
    assert response.status_code == 200





