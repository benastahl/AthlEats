import requests
s = requests.session()

def get_data():
    request_url = "http://httpbin.org/get"
    get_request = s.get(request_url)
    print(get_request)

if __name__ == '__main__':
    get_data()

