import argparse
import math
import time
import sys

class Segment:
    def __init__(self, left, right, phase, value, id):
        self.left = left
        self.right = right
        self.phase = phase
        self.value = value
        self.id = id


class Point:
    def __init__(self, x=0, y=0, phase=0, id=0):
        self.x = x
        self.y = y
        self.phase = phase
        self.id = id
    
    def __lt__(self, other):
        return (self.x, self.y, self.id) < (other.x, other.y, other.id)
    
    def __str__(self):
        return '{' + '(' + str(self.x) + ', ' + str(self.y) + ')' + ' : ' + str(self.phase) + '}'


def cross(o, p, q):
    return (p.x - o.x) * (q.y - o.y) - (p.y - o.y) * (q.x - o.x)


def find_starting_point(points):
    pos = -1
    for i in range(len(points)):
        if pos == -1 or (points[i] != None and points[i].y < points[pos].y):
            pos = i
    return pos


def sort_by_phase(points):
    best_point = []
    for point in points:
        while len(best_point) <= point.phase:
            best_point.append(None)
        if best_point[point.phase] == None:
            best_point[point.phase] = point
        best_point[point.phase] = min(best_point[point.phase], point)
    return list(reversed(best_point))


def lower_convex_hull(points):
    n = len(points)
    k = 0
    points.sort()
    hull = [None] * n
    if n < 3:
        return points
    for i in range(find_starting_point(points), n):
        while k >= 2 and cross(hull[k - 2], hull[k - 1], points[i]) <= 0:
            k -= 1
        hull[k] = points[i]
        k += 1
    return hull[:k]


def lower_convex_hull2(points):
    points = sort_by_phase(points)
    n = len(points)
    hull = [None] * n
    k = 0
    for i in range(find_starting_point(points), n):
        if points[i] == None:
            continue
        while k >= 2 and cross(hull[k - 2], hull[k - 1], points[i]) <= 0:
            k -= 1
        hull[k] = points[i]
        k += 1
    return hull[:k]


def seg_to_point(s):
    return Point((s.right - s.left) / 2, s.value, s.phase, s.id)


def get_points(segments):
    return list(map(seg_to_point, segments))


def get_pot_opt_points(segments):
    points = lower_convex_hull(get_points(segments))
    return list(map(lambda point: point.id, points))


class Rec:
    def __init__(self, arg=0, val=0):
        self.arg = arg
        self.val = val
    
    def __lt__(self, other):
        return (self.val, self.arg) < (other.val, other.arg)


def direct(func, lowb, upb, step_limit):
    segments = []
    record = Rec((lowb + upb) / 2, func((lowb + upb) / 2))
    segments.append(Segment(lowb, upb, 0, record.val, len(segments)))
    for _ in range(step_limit):
        good_points = get_pot_opt_points(segments)
        for i in good_points:
            s = segments[i]
            delta = (s.right - s.left) / 3
            c_left = s.left + delta / 2
            c_right = s.right - delta / 2
            res_left = func(c_left)
            res_right = func(c_right)
            record = min(record, min(Rec(c_left, res_left), Rec(c_right, res_right)))
            segments.append(Segment(s.left, s.left + delta, s.phase + 1, res_left, len(segments)))
            segments.append(Segment(s.right - delta, s.right, s.phase + 1, res_right, len(segments)))
            segments[i].left += delta
            segments[i].right -= delta
            segments[i].phase += 1
    return record


def ask_query(x):
    print("%.10f" % x, flush=True)
    return float(input())


# arg = 5.19977837 :: res = -1.60130755
# --area-begin 2.7 --area-end 7.5 --step-counter 100
def f1(x):
    return math.sin(x) + math.sin(10 * x / 3) + math.log(x) - 84 * x / 100 + 3


# arg = 17.03919896 :: res = -1.90596112
# --area-begin 3.1 --area-end 20.4 --step-counter 100
def f2(x):
    return math.sin(x) + math.sin(2 * x / 3)


# arg = -0.67957866 :: res = -0.82423940
# --area-begin -10 --area-end 10 --step-counter 100
def f4(x):
    return (x + math.sin(x)) * math.exp(-x * x)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read algorithm parameters')
    parser.add_argument('--area-begin', type=float, required=True)
    parser.add_argument('--area-end', type=float, required=True)
    parser.add_argument('--precision', type=float, required=False)
    parser.add_argument('--step-counter', type=int, required=True)
    args = parser.parse_args()
    
    start_time = time.time()
    result = direct(ask_query, args.area_begin, args.area_end, args.step_counter)
    end_time = time.time()

    print('STOP\n', "%.10f" % result.arg, sep='', flush=True)
    print("Time elapsed: %.5f" % (end_time - start_time), "s.", sep='', file=sys.stderr)
