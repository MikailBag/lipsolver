import argparse
from cmath import inf
import math
import time
import sys
import heapq


class Median:
    def __init__(self):
        self.left = []
        self.right = []
        self.med = None

    def push_left(self, x):
        heapq.heappush(self.left, -x)

    def push_right(self, x):
        heapq.heappush(self.right, x)

    def pop_left(self):
        return -heapq.heappop(self.left)

    def pop_right(self):
        return heapq.heappop(self.right)

    def fix(self):
        while len(self.left) + 1 < len(self.right):
            self.push_left(self.med)
            self.med = self.pop_right()
        while len(self.left) > len(self.right):
            self.push_right(self.med)
            self.med = self.pop_left()

    def add(self, x):
        if self.med is None:
            self.med = x
        elif x < self.med:
            self.push_left(x)
        elif x > self.med:
            self.push_right(x)
        else:
            if len(self.left) == len(self.right):
                self.push_right(x)
            else:
                self.push_left(x)
        self.fix()

    def get(self):
        return self.med


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


def calc_ang(p, q):
    if q.x == p.x:
        return inf
    return abs(q.y - p.y) / abs(q.x - p.x)


def get_pot_opt_points(segments, bound):
    points = lower_convex_hull(get_points(segments))
    n = len(points)
    if n > 1:
        res = []
        for i in range(n):
            k = 0
            if i == n - 1:
                k = calc_ang(points[i - 1], points[i])
            else:
                k = calc_ang(points[i], points[i + 1])
            if points[i].y - k * points[i].x <= bound:
                res.append(points[i])
        points = res
    return list(map(lambda point: point.id, points))


class Rec:
    def __init__(self, arg=0, val=0):
        self.arg = arg
        self.val = val
    
    def __lt__(self, other):
        return (self.val, self.arg) < (other.val, other.arg)


def direct(func, lowb, upb, step_limit, eps, improvement):
    median = Median()
    segments = []
    record = Rec((lowb + upb) / 2, func((lowb + upb) / 2))
    segments.append(Segment(lowb, upb, 0, record.val, len(segments)))
    median.add(record.val)
    for _ in range(step_limit):
        delta = 0
        if improvement == 0:
            delta = abs(record.val)
        elif improvement == 1:
            delta = median.get() - record.val
        else:
            delta = max(abs(record.val), median.get() - record.val)
        
        good_points = get_pot_opt_points(segments, record.val - eps * delta)
        
        if len(good_points) == 0:
            print('Steps used:', _, file=sys.stderr, flush=True)
            break
        for i in good_points:
            s = segments[i]
            delta = (s.right - s.left) / 3
            c_left = s.left + delta / 2
            c_right = s.right - delta / 2
            res_left = func(c_left)
            res_right = func(c_right)
            median.add(res_left)
            median.add(res_right)
            record = min(record, min(Rec(c_left, res_left), Rec(c_right, res_right)))
            segments.append(Segment(s.left, s.left + delta, s.phase + 1, res_left, len(segments)))
            segments.append(Segment(s.right - delta, s.right, s.phase + 1, res_right, len(segments)))
            segments[i].left += delta
            segments[i].right -= delta
            segments[i].phase += 1
    print('Function evaluations used:', func.counter, file=sys.stderr, flush=True)
    return record


def ask_query(x):
    ask_query.counter += 1
    print("%.12f" % x, flush=True)
    return float(input())


# arg = 5.19977837 :: res = -1.60130755
# --area-begin 2.7 --area-end 7.5 --step-counter 40 --max-slope 1
def f1(x):
    f1.counter += 1
    return math.sin(x) + math.sin(10 * x / 3) + math.log(x) - 84 * x / 100 + 3


# arg = 17.03919896 :: res = -1.90596112
# --area-begin 3.1 --area-end 20.4 --step-counter 40 --max-slope 1
def f2(x):
    f2.counter += 1
    return math.sin(x) + math.sin(2 * x / 3)


# arg = -0.67957866 :: res = -0.82423940
# --area-begin -10 --area-end 10 --step-counter 40 --max-slope 1
def f3(x):
    f3.counter += 1
    return (x + math.sin(x)) * math.exp(-x * x)


def init():
    ask_query.counter = 0
    f1.counter = 0
    f2.counter = 0
    f3.counter = 0


def solve(func, area_begin, area_end, step_counter, eps, improvement):
    start_time = time.time()
    result = direct(func, area_begin, area_end, step_counter, eps, improvement)
    end_time = time.time()

    print('STOP\n', '%.12f' % result.arg, sep='', flush=True)
    print('Time elapsed: %.12f' % (end_time - start_time), 's.', sep='', file=sys.stderr, flush=True)
    print('Final result of algorithm: %.12f' % result.val, sep='', flush=True)


def local_testing():
    eps = 1e-9
    steps = 12
    improvement = 2
    print('First function:', flush=True)
    solve(f1, 2.7, 7.5, steps, eps, improvement)
    print('Actual result: arg = 5.19977837 :: res = -1.60130755', flush=True)
    print()

    print('Second function:', flush=True)
    solve(f2, 3.1, 20.4, steps, eps, improvement)
    print('Actual result: arg = 17.03919896 :: res = -1.90596112', flush=True)
    print()

    print('Third function:', flush=True)
    solve(f3, -10, 10, steps, eps, improvement)
    print('Actual result: arg = -0.67957866 :: res = -0.82423940', flush=True)
    print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read algorithm parameters')
    parser.add_argument('--area-begin', type=float, required=True)
    parser.add_argument('--area-end', type=float, required=True)
    parser.add_argument('--precision', type=float, required=False)
    parser.add_argument('--step-counter', type=int, required=True)
    parser.add_argument('--max-slope', type=float, required=True)
    parser.add_argument('--epsilon', type=float, required=True)
    # parser.add_argument('--improvement', type=int, required=True)
    args = parser.parse_args()

    init()

    # local_testing()

    solve(ask_query, args.area_begin, args.area_end, args.step_counter, args.epsilon, 2)
