import requests as req
import json

def skypicker_api_call(requestURL,parameters):
    response = req.get(url=requestURL,params=parameters)
    if response.status_code != 200:
        print(response.json())
        exit()
    data = response.json()
    return json.dumps(data)

def get_flight_data(fly_from,fly_to,date_from,date_to,max_stopovers,partner,sort,distance):
    requestURL = "https://api.skypicker.com/flights"
    parameters = {"fly_from" : fly_from, "fly_to" : fly_to,"date_from" : date_from,"date_to" : date_to,"max_stopovers" : max_stopovers,"partner" : partner,"sort" : sort,"distance" : distance}
    return skypicker_api_call(requestURL, parameters)
    
def main():
    fly_from = "LCA"
    fly_to = "BEY"
    date_from = "01/01/2019"
    date_to = "01/02/2019"
    max_stopovers = "0"
    partner = "picky"
    sort = "date"
    distance = ""
    flight_data = get_flight_data(fly_from,fly_to,date_from,date_to,max_stopovers,partner,sort,distance)
    data = json.loads(flight_data)
    print(json.dumps(data["data"]))


main()

