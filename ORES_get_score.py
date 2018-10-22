import os
import csv
import json
import requests


def get_data(id_list):
    """ pasing the response from server"""
    id_list_str = ''
    for i in range(len(id_list)-1):
        id_list_str += str(id_list[i]) + '|'
    id_list_str += str(id_list[-1])

    url = 'https://ores.wikimedia.org/v3/scores/wikidatawiki/?revids=' + id_list_str
    request = requests.get(url)

    result = []

    for id in id_list:
        entry = list_get(json.loads(request.text), 'wikidatawiki.scores.' + id)
        list = [id]
        keys = [
            'damaging.score.prediction',
            'damaging.score.probability.true',
            'damaging.score.probability.false',
            'goodfaith.score.prediction',
            'goodfaith.score.probability.true',
            'goodfaith.score.probability.false',
            'itemquality.score.prediction'
        ]

        for key in keys:
            list.append(list_get(entry, key))

        result.append(tuple(list))

    return result


def put_csv(filename, data):
    """ write in csv file with parsed data"""
    file_exists = os.path.isfile(filename)
    with open(filename, 'a+') as f:
        output = csv.writer(f)
        if not file_exists:
            output.writerow([
                'rev_id','damaging_prediction',
                'damaging_value_true',
                'damaging_value_false',
                'goodfaith_prediction',
                'goodfaith_value_true',
                'goodfaith_value_false',
                'itemquality_prediction'
            ])

        for row in data:
            output.writerow(row)


def get_csv(filename, n):
    """ transforming the csv input into list"""
    with open(filename) as f:
        input = csv.reader(f)
        list = []
        for index, line in enumerate(input):
            list.append(line[0])
            if index == n-1:
                break
    return list


def list_get(list, key):
    """The list_get function retrieves a value from a deeply nested array using "dot" notation."""
    new_list = list.copy()
    keys = key.split('.')
    for key in keys:
        new_list = new_list[key]

    return new_list


def main():
    start = 1277050   #the number of processed scores till now
    end = 2000000
    data = []
    id_list = get_csv('rev_ids_for_ores.csv', end)
    print('ja')

    for i in range(start, end, 50):
        try:
            data += get_data(id_list[i:i + 50])
            print('lala')
        except (RuntimeError, TypeError, NameError, KeyError):
            pass

    put_csv('csvfile.csv', data)





if __name__ == "__main__":
    main()
