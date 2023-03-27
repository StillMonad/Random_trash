import time
import requests
from collections import deque

url = "https://api.binance.com"
api_price = "/api/v3/ticker/price?symbol="
BTC = "BTCUSDT"
ETH = "ETHUSDT"

LOG_TIME = 3600  # sec
DIFF_ALERT = 1.0  # %

last_max = 0

r = 0.9631582183058636  # коэффициент корреляции вычисленный в прошлой задаче
# кстати он тут едва ли уместен, так как там была корреляция за день, а тут за ~1 cекунду.


def get_last(d: deque):
    """
    Возвращает список значений за последние LOG_TIME секунд
    """
    last = d[-1]
    i = len(d) - 2
    arr = [last]
    while i >= 0:
        if last['time'] - d[i]['time'] > LOG_TIME:
            break
        arr = [d[i]] + arr
        i -= 1
    return arr


def alert(arr):
    """
    Выводит наибольшую разницу между текущим значением и пердудущими значениеми за выбранное LOG_TIME\n
    Если разница превышает DIFF_ALERT, то выводит ALERT
    """
    global last_max
    # в прошлой задаче уже писал: я не уверен, что собственные движения считаются именно так
    # массив цен ETH с вычетом влияния BTC
    eth_real = [e['eth'] - e['eth'] * (e['change_btc'] * r / 100) for e in arr]
    last = eth_real[-1]
    alert = False
    max_change = 0
    for i in range(len(arr) - 2, 0, -1):
        change = (1 - last / eth_real[i])
        if abs(change) > DIFF_ALERT / 100:
            if change == last_max:
                return
            last_max = change
            print(f"ALERT: изменение за {LOG_TIME} секунд превысило ±{DIFF_ALERT}%:    ", end='')
            print("{:+2.15f} %".format(change * 100))
            return
        max_change = max_change if abs(max_change) > abs(change) else change
    if max_change == last_max:
        return
    last_max = max_change
    print("Максимальное изменение за {} секунд:    {:+2.15f} %".format(LOG_TIME, max_change))


if __name__ == '__main__':
    btc_price = float(requests.get(url + api_price + BTC).json()['price'])
    eth_price = float(requests.get(url + api_price + ETH).json()['price'])
    d = {'time': time.time(), 'btc': btc_price, 'change_btc': 0, 'eth': eth_price, 'change_eth': 0}
    values = deque()
    values.append(d)

    while True:
        btc_price = float(requests.get(url + api_price + BTC).json()['price'])
        eth_price = float(requests.get(url + api_price + ETH).json()['price'])
        curr_time = time.time()
        change_btc = 100 * (btc_price - values[-1]['btc']) / btc_price
        change_eth = 100 * (eth_price - values[-1]['eth']) / eth_price
        d = {'time': curr_time, 'btc': btc_price, 'change_btc': change_btc, 'eth': eth_price, 'change_eth': change_eth}
        values.append(d)
        last_n = get_last(values)
        for i in range(len(values) - len(last_n)):
            values.popleft()  # очищаем очередь от значений старше LOG_TIME
        alert(last_n)
