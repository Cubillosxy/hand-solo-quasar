from fastapi.testclient import TestClient


from main import app
from models import Satellite, TxResponse, SatelliteBase
from utils import Trilateration
from utils import TOP_SECRECT, TOP_SECRECT_SPLIT, BASE_URL
import random


client = TestClient(app)
xo, yo = random.randint(-500, 500), random.randint(-500, 500)
tx_location = (xo, yo)
satellites_list = Trilateration.get_satellites_list()


def test_not_enought_data():
    s1 = Satellite(name='test', distance=1, message=['test'])
    data = {
        "satellites": [s1.dict()]
    }
    response = client.post(TOP_SECRECT, json=data)
    assert response.status_code == 404
    assert response.json() == {
        "error": Trilateration.ERROR_NOT_ENOUGH_DATA
    }



def test_invalid_data():
    s1 = Satellite(name='test', distance=1, message=['test'])
    data = {
        "satellites": [s1.dict() for i in range(3)]
    }
    response = client.post(TOP_SECRECT, json=data)
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

        } for i in satellites_list
    ]

    data = {
        "satellites": satellites
    }
    response = client.post(TOP_SECRECT, json=data)
    assert response.status_code == 404
    assert response.json() == {
        "error": Trilateration.ERROR_UNABLE_GET_MESSAGE
    }


def test_unable_to_get_location():
    satellites = [
        {
            'distance': Trilateration.distance_x_y(tx_location, [i['value']])['value'] - random.randint(300, 600),
            'message': ['very', 'easy'],
            'name': i['name']

        } for i in satellites_list
    ]
    data = {
        "satellites": satellites
    }
    response = client.post(TOP_SECRECT, json=data)

    print('location', tx_location)

    assert response.status_code == 404
    assert response.json() == {
        "error": Trilateration.ERROR_UNABLE_GET_LOCATION
    }

def test_repeat_msg():

    good_msg = ['test', 'my', 'app', 'ok']
    satellites = [
        {
            'distance': Trilateration.distance_x_y(tx_location, [i['value']])['value'],
            'message': good_msg,
            'name': i['name']

        } for i in satellites_list
    ]

    data = {
        "satellites": satellites
    }
    response = client.post(TOP_SECRECT, json=data)
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

    #offset message
    good_3 = ['my', 'app', 'ok']
    mgs3 = [
        ['', 'my', '', 'ok'],
        ['my', 'app', ''],
        ['', 'my', '', 'ok'],
    ]

    mgs4 = [
        [ 'my', '', 'ok'],
        ['my', 'app', '', ''],
        [ 'my', '', 'ok'],
    ]

    mgs5 = [
        [ 'my', '', ''],
        ['', 'app', ''],
        [ '', '', 'ok'],
    ]


    _custom1 = []
    _custom2 = []
    _custom3 = []
    _custom4 = []
    _custom4 = []
    _custom5 = []

    for i, j in enumerate(satellites_list):
        _aux = {
            'distance': Trilateration.distance_x_y(tx_location, [j['value']])['value'],
            'name': j['name'],
            'message': mgs1[i]
        }

        _custom1.append(_aux)
        _aux = dict(_aux)
        _aux['message'] = mgs2[i]
        _custom2.append(_aux)
        _aux = dict(_aux)
        _aux['message'] = mgs3[i]
        _custom3.append(_aux)
        _aux = dict(_aux)
        _aux['message'] = mgs4[i]
        _custom4.append(_aux)
        _aux = dict(_aux)
        _aux['message'] = mgs5[i]
        _custom5.append(_aux)

    list_cases = [_custom1, _custom2, _custom3, _custom4, _custom5]
    list_response = [good_1, good_1, good_3, good_3, good_3]

    for i, j in enumerate(list_cases):
        response = client.post(TOP_SECRECT, json={"satellites": j})
        assert response.status_code == 200

        assert response.json() == {
            'message' :' '.join(list_response[i]),
            'position': {'x': float(xo), 'y': float(yo)}
        }



def test_split():
    satellite_base = SatelliteBase(distance=2, message=['test', ])
    response = client.post(TOP_SECRECT_SPLIT + 'invalid', json=satellite_base.dict())
    assert response.status_code == 200
    assert response.json() == {"message": "Tomato"}



