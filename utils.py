
from multiprocessing import Pool
import os

TOP_SECRECT = '/topsecrect/'
TOP_SECRECT_SPLIT = '/topsecret_split/'
SECRECT_KEY = os.environ.get('SECRECT_KEY', 'test')
BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1')
MIN_DATA_LENGTH = 3

class Satellites(object):


    def __init__(self):
        self.satellites_list = self.get_satellites_list()
        self.satellites = [i['value'] for i in self.satellites_list]
    

    @staticmethod
    def get_satellites_list():
        KENOBI = { 'name': 'kenobi', 'value': (-500, -200)}
        SKYWALKER = { 'name': 'skywalker', 'value': (100, -100)}
        SATO = { 'name': 'sato', 'value': (500, 100)}

        return [KENOBI, SKYWALKER, SATO]

    @staticmethod
    def get_satellites_names(satellites_list):
        return { i['name']: i for i in satellites_list if i.get('name')}


    def _get_satellites_names(self):
        return self.get_satellites_names(self.satellites_list)


#assumptions
#we assume that we are receiving the positions sorted according the SATELLITES



class Trilateration(Satellites):
    distances = None
    messages = None
    
    ERROR_NOT_ENOUGH_DATA = 'Not enough data'
    ERROR_INVALID_DATA = 'invalid data'
    ERROR_INVALID_DATA_LENGHT = 'Invalid data lenght'
    ERROR_UNABLE_GET_MESSAGE = 'Unable to resolve message'
    ERROR_UNABLE_GET_LOCATION = 'Unable to resolve location'
    ERROR_CORRUPTED_DATA = 'Corrupt data '

    def __init__(self, input_data):
        self.input_data = input_data
        super().__init__()


    def set_data(self, standarized=False):

        dict_satellites = self.input_data

        if not standarized:
            if len(self.input_data) < MIN_DATA_LENGTH:
                return self.ERROR_NOT_ENOUGH_DATA

            dict_satellites = self.get_satellites_names(self.input_data)

        _distances = []
        _messages = []
        for key in self.satellites_list:
            _name = key['name']
            values = dict_satellites.get(_name, None)
            if values is not None:
                _distances.append(values['distance'])
                _messages.append(values['message'])

        self.distances = _distances
        self.messages = _messages
        

    def prepare(self, standarized=False):
        if not standarized and not isinstance(self.input_data, list):
            return self.ERROR_INVALID_DATA

        data_error = self.set_data(standarized=standarized)


        if data_error:
            return data_error

        if len(self.distances) < MIN_DATA_LENGTH:
            return self.ERROR_INVALID_DATA_LENGHT


    def prepare_standarized(self):

        if not isinstance(self.input_data, dict):
            return self.ERROR_INVALID_DATA


        result = { 
            key: {
                **item,
                'name': key
            }
            for key, item in self.input_data.items()
        }

        self.input_data = result

        return self.prepare(standarized=True)
        

    @staticmethod
    def circle_intersection(circle1: tuple, circle2: tuple):
        '''
        based on  https://gist.github.com/xaedes/974535e71009fa8f090e
        :param circle1:  tuple(x,y,radius)
        :param circle2:  tuple(x,y,radius)
        :return: tuple of intersection points (which are (x,y) tuple)
        '''
        x1, y1, r1 = circle1
        x2, y2, r2 = circle2
        # d is euclidean distance between circle centres
        dx, dy = x2 - x1, y2 - y1
        d = (dx**2 + dy**2)**0.5
        if (d > r1 + r2) or (d < abs(r1 - r2)) or (d == 0 and r1 == r2):
            # 'No solutions, the circles are separate.'
            #  No solutions because one circle is contained within the other
            #  infinite number of solutions.
            return None

        a = (r1*r1 - r2*r2 + d**2) / (2*d)
        h = (r1*r1 - a**2)**0.5
        xm = x1 + a*dx/d
        ym = y1 + a*dy/d
        xs1 = xm + h*dy/d
        xs2 = xm - h*dy/d
        ys1 = ym - h*dx/d
        ys2 = ym + h*dx/d

        return (xs1, ys1), (xs2, ys2)


    @staticmethod
    def distance_x_y(x_y: tuple, points: list):

        result = 0
        
        for i in points:
            dx = i[0] - x_y[0]
            dy = i[1] - x_y[1]
            if dx != 0 or dy != 0:
                result += (dx**2 + dy**2)**0.5

        return {'key': x_y, 'value': result}


    def get_intersection_points(self, distances):
        args_quantity = len(distances)
        
        if args_quantity < 3:
            return None
        
        intersection_points = ()
        for i in range(0, args_quantity - 1):
            for j in range(i+1, args_quantity):
                _x, _y = self.satellites[i]
                _xo, _yo = self.satellites[j]
                result = self.circle_intersection((_x, _y, distances[i]), (_xo, _yo, distances[j]))
                if result is not None:
                    intersection_points += result

        return intersection_points

    def _get_location(self, distances):
        
        intersection_points = self.get_intersection_points(distances)

        if not intersection_points or len(intersection_points) < MIN_DATA_LENGTH * 2:
            return None

        with Pool(processes=6) as pool:
            result = pool.starmap(self.distance_x_y, [ (i, intersection_points) for i in intersection_points])

        point = min(result, key=lambda x: x['value'])['key']
        # round response acceptin error +- 0.5

        return round(point[0], 1), round(point[1], 1)


    def get_location(self):
        return self._get_location(self.distances)

    @staticmethod
    def _merge_msg(base_message, m2):
        m1_len = len(base_message)
        m2_len = len(m2)
        list_words = [str(i).strip() for i in base_message if i]

        if m1_len > m2_len:
            for w in m2:
                # find offset 
                if w in list_words:
                    index_m2 = m2.index(w)
                    index_m1 = base_message.index(w)
                    index_diff = index_m1 - index_m2
                    return [str(base_message[i+index_diff]).strip() or str(m2[i]).strip() for i in range(m2_len)]

        else: # equal
            return [str(base_message[i]).strip() or str(m2[i]).strip() for i in range(m1_len)]

    @classmethod
    def _get_message(cls, messages):

        base_msg = max(messages, key=len)

        # all msg are equal
        if not messages:
            return base_msg

        for row in messages:
            if base_msg != row:
                base_msg = cls._merge_msg(base_msg, row)

        return base_msg 

    def get_message(self):
        msg = self._get_message(self.messages)
        if len(msg) != len([i for i in msg if i]):
            return None

        return ' '.join(msg) 

