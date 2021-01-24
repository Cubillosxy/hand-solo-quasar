
from multiprocessing import Pool


KENOBI = (-500, -200)
SKYWALKER = (100, -100)
SATO = (500, 100)

error_value = 1

#assumptions
#center the plane over one point
#we assume that we are receiving the positions sorted according the satelites


offset_x, offset_y = SKYWALKER
#SKYWALKER = {'position': (0, 0)}

SATELITES = [KENOBI, SKYWALKER, SATO]



def circle_intersection(circle1, circle2):
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


def distance_x_y(x_y, points):

    result = 0
    
    for i in points:
        dx = i[0] - x_y[0]
        dy = i[1] - x_y[1]
        result += (dx**2 + dy**2)**0.5

    return {'key': x_y, 'value': result}


def get_intersection_points(distances):
    args_quantity = len(distances)
    
    if args_quantity < 3:
        return None
    
    intersection_points = ()
    for i in range(0, args_quantity - 1):
        for j in range(i+1, args_quantity):
            _x, _y = SATELITES[i]
            _xo, _yo = SATELITES[j]
            result = circle_intersection((_x, _y, distances[i]), (_xo, _yo, distances[j]))
            if result is not None:
                intersection_points += result

    return intersection_points

def get_location(distances):
    
    intersection_points = get_intersection_points(distances)

    if not intersection_points or len(intersection_points) < 6:
        return None

    with Pool() as pool:
        result = pool.starmap(distance_x_y, [ (i, intersection_points) for i in intersection_points])

    point = min(result, key=lambda x: x['value'])
    
    return point['key']


def _merge_msg(m1, m2):
    result = [m1[i].strip() or m2[i].strip() for i in range(len(m1))]

def get_message(messages):
    msg_len = len(messages)

    base_msg = max(messages, key=len)
    len_base = len(base_msg)


    list_words = [i.strip() for i in base_msg if i]
    output = list(base_msg)

    _messages = list(messages).remove(base_msg)



    dict_result = {}
    count = 0
    for i in range(0, msg_len - 1):
        for j in range(i+1, msg_len):
            _msg = messages[i]
            _target = messages[j]
            len_key = len(_msg)
            
            if len_key == len(_target):
                if len_key in dict_result:
                    _msg = dict_result[len_key]
                merge = _merge_msg(_msg, _target)
                dict_result[len_key] = merge
                count += 1
            
            if count == msg_len -1:
                break
        if count == msg_len -1:
            break
    
    # all messages has same length 
    if count == msg_len -1:
        return dict_result[len_base]


    
    for row in _messages:
        target = row
        if len(base_msg) != len(row):
            


    result = []
    for j in range(len(base_msg)):
        outs = []
        for i in messages:
            try:
                if i[j].strip():
                    outs.append(i[j])

            except IndexError:
                break

        _aux = outs[0] if outs else ''
        result.append(_aux)

    if len(base_msg) != len(result):
        return None

    return result

