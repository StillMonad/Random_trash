import csv
import numpy as np

# данные в приложенных файлах взяты за последний год
btc_fname = "BTC_USD.csv"
eth_fname = "ETH_USD.csv"


def get_data(fname):
    ret = []
    with open(fname) as f:
        spamreader = csv.reader(f, delimiter=',')
        for row in spamreader:
            ret.append(row)
    return ret


if __name__ == '__main__':
    btc_data = get_data(btc_fname)[1:]
    eth_data = get_data(eth_fname)[1:]

    btc_open = np.array([float(line[1].replace(',', '')) for line in btc_data])
    eth_open = np.array([float(line[1].replace(',', '')) for line in eth_data])

    r = np.corrcoef(eth_open, btc_open)[0][1]  # r = 0.9631582183058636 - очень сильная прямая корреляция
    print(f"Коэффициент корреляции r = {r}")

    btc_change = np.array([float(line[6].replace('%', '')) for line in btc_data])
    eth_change = np.array([float(line[6].replace('%', '')) for line in eth_data])
    dates = np.array([line[0] for line in eth_data])

    print(f"Собственные движения цен ETH:")
    for i in range(len(btc_data)):
        print("{:>12}: ".format(dates[i]), end="")
        # Предполагаю, что можно а считать так: (как правильно я не уверен)
        change = eth_change[i] - btc_change[i] * r
        print("{:+5.5f}".format(change))
