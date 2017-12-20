import math

def cycle_predictor(a, n):
    if len(a) < n:
        return None
    return a[len(a)-n]


def moving_average(a, n):
    if len(a) < n:
        return None
    return float(sum(a[len(a)-n:])) / n


def round_average(a, n):
    if len(a) < n:
        return None
    return int(moving_average(a, n))


def seasonal_naive_predictor(a, n):
    if len(a) < n:
        return None
    result = 0
    for index in range(n-1, len(a), n):
        if index < len(a):
            result = a[index]
            index = index + n
    return result


def helper_exponential(a, n):
    forecasts = list(range(0, len(a)+1))
    forecasts[0] = a[0]
    for i in range(1, len(a)+1):
        forecasts[i] = n * a[i-1] + (1-n) * forecasts[i-1]
    return forecasts


def exponential(a, n, times):
    data = a
    for i in range(0, times):
        data = helper_exponential(data, n)
    return data[-1]


def drift(a):
    parameter = (a[-1] - a[0]) / float(len(a))
    return parameter * (len(a)+1) + a[0]


def extrapolation(a):
    if len(a) < 3:
        return None
    return 2 * a[-1] - a[-2]


def geometric_moving_average(a, period):
    final_sum = 0
    limit = len(a) - period
    if (limit-1) < 0:
        return None
    for i in range(len(a)-1, (limit-1), -1) :
        # TODO: check math.log(0)
        if a[i] != 0:
            final_sum += math.log(a[i])
        else:
            pass
    return math.exp(final_sum/period)


def helper_triangular_moving_average(a, period):
    final_sum = 0.0
    limit = len(a) - period
    for i in range(len(a)-1, (limit-1), -1):
        final_sum += a[i]
    return final_sum/period


def triangular_moving_average(a, period):
    final_sum = 0
    if len(a) - period < 0: return None
    for i in range(1, period+1):
        final_sum += helper_triangular_moving_average(a, i)
    return final_sum/period


def polynomial(a):
    # TODO: problem after some values
    ns = 0
    xx = range(1, len(a)+1)
    hh = abs(11 - xx[0])
    c = []; d = []; dd = []
    for i in range(0, len(xx)):
        h = abs(11-xx[i])
        if h == 0:
            dy = 0.0
        elif h < hh:
            ns = i
            hh = h
        c.append(a[i])
        d.append(a[i] + 1.e-99)
    y = a[ns]
    ns = ns - 1
    for m in range(1, len(xx)):
        for i in range(0, len(a)-m):
            w = c[i+1] - d[i]
            h = abs(xx[i+m]-11)
            # TODO: check division by zero
            if h == 0:
                return None
            else:
                t = (xx[i]-11) * (d[i]/h)
            dd = t - c[i+1]
            if dd == 0:
                return None
            else:
                dd = w/dd
            d[i] = c[i+1] * dd
            c[i] = t*dd
        if (2 * (ns+1)) < (len(a)- m):
            dy = c[ns+1]
        else:
            dy = d[ns]
            ns -= 1
        y = y + dy
    return y


def parabolic_average_predictor(a, trend, step):
    sar = [a[0]]; high = a[0]; low = a[0]
    for i in range(1, len(a)+1):
        if (a[i-1]> high):
            sar.append(a[i-1] + (trend* abs(high-a[i-1])))
            high = a[i-1]
            trend += step
        elif a[i-1]< high and a[i-1]>low:
            sar.append(a[i-1] + (trend*abs(high-a[i-1])))
        else:
            sar.append(a[i-1] + (trend*abs(low-a[i-1])))
            low = a[i-1]
            trend += step
    return sar[-1]


def linear_regression(a):
    sumx = 0.0; sumx2 = 0.0; sumy = 0.0; sumxy = 0.0
    for i in range(0, len(a)):
        sumx += a[i]
        sumx2 += a[i] * a[i]
        sumy += i
        sumxy += a[i] * i
    mean_x = sumx / len(a)
    mean_y = sumy / len(a)
    if (sumx2 - sumx * mean_x) == 0: return None
    slope = (sumxy - sumx*mean_y) / (sumx2 - sumx * mean_x)
    intercept = mean_y - slope * mean_x
    if slope == 0: return None
    return (len(a)-intercept) / slope


def linear_prediction(a):
    dat = list(a)
    dat.append(0)
    l = [[0 for i in range(len(a)+1)] for i in  range(len(a)+1)]
    l[0][0] = 1; l[1][1] = 1
    if dat[0] ==0:
        return None
    l[1][0] = (-dat[1]) / float(dat[0])
    e = [0 for i in range(len(a)+1)]
    e[0] = dat[0]
    e[1] = e[0] * (1 - l[1][0] * l[1][0])
    for i in range(2, len(a)):
        gap = 0
        for k in range(0, i):
            gap += dat[k+1] * l[i-1][k]
        if e[i-1] == 0:
            return None
        gamma = gap / e[i-1]
        l[i][0] = -gamma
        for k in range(1, i):
            l[i][k] = l[i-1][k-1] - gamma * l[i-1][i - 1 - k]
        l[i][i] = 1
        e[i] = e[i - 1] * (1. - gamma * gamma)
    coeffs = []
    coeffs.append(1)
    for i in range(1, len(a)-1):
        coeffs.append(l[len(a)-1][len(a) - i - 1])
    sum_coeffs = sum(coeffs)
    for i in range(0, len(coeffs)):
        if sum_coeffs == 0:
            return None
        coeffs[i] = coeffs[i] / sum_coeffs
    result = 0
    for i in range(0, len(coeffs)):
        result += coeffs[i] * dat[i]
    return result


TARGET_VALUE = 0
K_PLUS = 0.1
K_MINUS = .1
H_PLUS = 1.0
H_MINUS = 1.0

def fusion(list_values):
    target = sum(filter(None, list_values)) / sum(1 for i in  list_values if i != None) + TARGET_VALUE
    r = 0;q=0;fusion_result=0.0;accepted=0;
    results = []
    for value in list_values:
        if value == None:
            results.append(1)
            continue
        outValue = 0
        r = max(0, (value - (target + K_PLUS) + r))
        q = min(0, (value - (target - K_MINUS) + q))
        if  r > H_PLUS:
            outValue = 1
            r = 0.0
        if q < -H_MINUS:
            outValue = 1
            q = 0.0
        if outValue == 0:
            accepted += 1
            fusion_result += value
        results.append(outValue)
    if accepted !=0:
        return fusion_result/accepted
    return list_values[0]


def KDE(t, expected_value, last_measurement):
    if t == 1:
        return last_measurement
    return (((t - 1.0) / t) * expected_value ) + ((1.0 / t) * last_measurement)import math

def cycle_predictor(a, n):
    if len(a) < n:
        return None
    return a[len(a)-n]


def moving_average(a, n):
    if len(a) < n:
        return None
    return float(sum(a[len(a)-n:])) / n


def round_average(a, n):
    if len(a) < n:
        return None
    return int(moving_average(a, n))


def seasonal_naive_predictor(a, n):
    if len(a) < n:
        return None
    result = 0
    for index in range(n-1, len(a), n):
        if index < len(a):
            result = a[index]
            index = index + n
    return result


def helper_exponential(a, n):
    forecasts = list(range(0, len(a)+1))
    forecasts[0] = a[0]
    for i in range(1, len(a)+1):
        forecasts[i] = n * a[i-1] + (1-n) * forecasts[i-1]
    return forecasts


def exponential(a, n, times):
    data = a
    for i in range(0, times):
        data = helper_exponential(data, n)
    return data[-1]


def drift(a):
    parameter = (a[-1] - a[0]) / float(len(a))
    return parameter * (len(a)+1) + a[0]


def extrapolation(a):
    if len(a) < 3:
        return None
    return 2 * a[-1] - a[-2]


def geometric_moving_average(a, period):
    final_sum = 0
    limit = len(a) - period
    if (limit-1) < 0:
        return None
    for i in range(len(a)-1, (limit-1), -1) :
        # TODO: check math.log(0)
        if a[i] != 0:
            final_sum += math.log(a[i])
        else:
            pass
    return math.exp(final_sum/period)


def helper_triangular_moving_average(a, period):
    final_sum = 0.0
    limit = len(a) - period
    for i in range(len(a)-1, (limit-1), -1):
        final_sum += a[i]
    return final_sum/period


def triangular_moving_average(a, period):
    final_sum = 0
    if len(a) - period < 0: return None
    for i in range(1, period+1):
        final_sum += helper_triangular_moving_average(a, i)
    return final_sum/period


def polynomial(a):
    # TODO: problem after some values
    ns = 0
    xx = range(1, len(a)+1)
    hh = abs(11 - xx[0])
    c = []; d = []; dd = []
    for i in range(0, len(xx)):
        h = abs(11-xx[i])
        if h == 0:
            dy = 0.0
        elif h < hh:
            ns = i
            hh = h
        c.append(a[i])
        d.append(a[i] + 1.e-99)
    y = a[ns]
    ns = ns - 1
    for m in range(1, len(xx)):
        for i in range(0, len(a)-m):
            w = c[i+1] - d[i]
            h = abs(xx[i+m]-11)
            # TODO: check division by zero
            if h == 0:
                return None
            else:
                t = (xx[i]-11) * (d[i]/h)
            dd = t - c[i+1]
            if dd == 0:
                return None
            else:
                dd = w/dd
            d[i] = c[i+1] * dd
            c[i] = t*dd
        if (2 * (ns+1)) < (len(a)- m):
            dy = c[ns+1]
        else:
            dy = d[ns]
            ns -= 1
        y = y + dy
    return y


def parabolic_average_predictor(a, trend, step):
    sar = [a[0]]; high = a[0]; low = a[0]
    for i in range(1, len(a)+1):
        if (a[i-1]> high):
            sar.append(a[i-1] + (trend* abs(high-a[i-1])))
            high = a[i-1]
            trend += step
        elif a[i-1]< high and a[i-1]>low:
            sar.append(a[i-1] + (trend*abs(high-a[i-1])))
        else:
            sar.append(a[i-1] + (trend*abs(low-a[i-1])))
            low = a[i-1]
            trend += step
    return sar[-1]


def linear_regression(a):
    sumx = 0.0; sumx2 = 0.0; sumy = 0.0; sumxy = 0.0
    for i in range(0, len(a)):
        sumx += a[i]
        sumx2 += a[i] * a[i]
        sumy += i
        sumxy += a[i] * i
    mean_x = sumx / len(a)
    mean_y = sumy / len(a)
    if (sumx2 - sumx * mean_x) == 0: return None
    slope = (sumxy - sumx*mean_y) / (sumx2 - sumx * mean_x)
    intercept = mean_y - slope * mean_x
    if slope == 0: return None
    return (len(a)-intercept) / slope


def linear_prediction(a):
    dat = list(a)
    dat.append(0)
    l = [[0 for i in range(len(a)+1)] for i in  range(len(a)+1)]
    l[0][0] = 1; l[1][1] = 1
    if dat[0] ==0:
        return None
    l[1][0] = (-dat[1]) / float(dat[0])
    e = [0 for i in range(len(a)+1)]
    e[0] = dat[0]
    e[1] = e[0] * (1 - l[1][0] * l[1][0])
    for i in range(2, len(a)):
        gap = 0
        for k in range(0, i):
            gap += dat[k+1] * l[i-1][k]
        if e[i-1] == 0:
            return None
        gamma = gap / e[i-1]
        l[i][0] = -gamma
        for k in range(1, i):
            l[i][k] = l[i-1][k-1] - gamma * l[i-1][i - 1 - k]
        l[i][i] = 1
        e[i] = e[i - 1] * (1. - gamma * gamma)
    coeffs = []
    coeffs.append(1)
    for i in range(1, len(a)-1):
        coeffs.append(l[len(a)-1][len(a) - i - 1])
    sum_coeffs = sum(coeffs)
    for i in range(0, len(coeffs)):
        if sum_coeffs == 0:
            return None
        coeffs[i] = coeffs[i] / sum_coeffs
    result = 0
    for i in range(0, len(coeffs)):
        result += coeffs[i] * dat[i]
    return result


TARGET_VALUE = 0
K_PLUS = 0.1
K_MINUS = .1
H_PLUS = 1.0
H_MINUS = 1.0

def fusion(list_values):
    target = sum(filter(None, list_values)) / sum(1 for i in  list_values if i != None) + TARGET_VALUE
    r = 0;q=0;fusion_result=0.0;accepted=0;
    results = []
    for value in list_values:
        if value == None:
            results.append(1)
            continue
        outValue = 0
        r = max(0, (value - (target + K_PLUS) + r))
        q = min(0, (value - (target - K_MINUS) + q))
        if  r > H_PLUS:
            outValue = 1
            r = 0.0
        if q < -H_MINUS:
            outValue = 1
            q = 0.0
        if outValue == 0:
            accepted += 1
            fusion_result += value
        results.append(outValue)
    if accepted !=0:
        return fusion_result/accepted
    return list_values[0]


def KDE(t, expected_value, last_measurement):
    if t == 1:
        return last_measurement
    return (((t - 1.0) / t) * expected_value ) + ((1.0 / t) * last_measurement)
