[![Build Status](https://travis-ci.com/EUGINELETHAL/Order-Api.svg?branch=main)](https://travis-ci.com/EUGINELETHAL/Backend-challenge)
[![Coverage Status](https://coveralls.io/repos/github/EUGINELETHAL/Order-Api/badge.svg?branch=main)](https://coveralls.io/github/EUGINELETHAL/Order-Api?branch=main)
# LOGISTICS-API
Logistics-Api is a simple REST  API used to upload customers orders.

..User Stories  <br /> <br /> 
Users authenticates via OAUTH2 and OpenidCOnnect(GOogleOAuth 2.0 ) <br />
Customer creates order  <br />
Customers gets message after order created sucessfully(Asynchronous  Task) <br />

# Tools and Technologies
1. Django <br />
2. DjangoRest <br />
3. Travis(CI/CD) <br />
4. Heroku-Deployment <br />
5. AfricaisTalking-(SMSGATEWAY) <br />
6. Coverage <br />
7. Celery <br />
8. Redis <br />
9. Pytest <br />
10. Docker <br />
11. Google OR-tools <br />
11. Docker-Compose <br />
12.Google OR-tools<br />
13
## API ENDPOINTS

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/470df32a30646e961eb9)
#### Question Endpoints.
| API Endpoint  | Description | Methods |
| ------------- | ------------- | ------------- |
| /api/v1/delivery/ |Get all deliveries  | GET  |
  api/v1/delivery/  | create customer  | POST |
| /api/v1/delivery/1  |Detail Delivery  | GET  |
  /api/v1/route/Create| Create Route || POST  |
 /api/v1/route/1| Create Route | POST  |
/api/v1/route/1 | Route Detail | GET |
https://developers.google.com/maps/documentation/javascript/examples/polyline-simple

api/v1/delivery
api/v1/delivery/export_deliveries
api/v1/delivery/export_deliveries
api/v1/delivery/
api/v1/delivery/
api/v1/delivery/

Endpoints:
----------

### Get all Deliveries

`GET api/v1/delivery`

Example request body:

```source-json
{
  "user":{
    "email": "jake@jake.jake",
    "password": "jakejake"
  }
}
```

No authentication required, returns a User

Required fields: `email`, `password`

```source-json
[
    {
        "id": 3,
        "code": "DELRM8D7A",
        "address": "Kiserian",
        "cordinates": [
            -1.4308204984641613,
            36.6778564402076
        ],
        "status": "pending"
    },
    {
        "id": 4,
        "code": "DEL3I1KSR",
        "address": "Ruiru",
        "cordinates": [
            -1.1425024035472517,
            36.964874262432765
        ],
        "status": "pending"
    },
    {
        "id": 5,
        "code": "DELYGVMWY",
        "address": "Thika",
        "cordinates": [
            -1.0271666544093947,
            37.067871088589584
        ],
        "status": "pending"
    },
    {
        "id": 6,
        "code": "DELCP34NU",
        "address": "Ongata Rongai",
        "cordinates": [
            -1.3951257895566065,
            36.76025390113323
        ],
        "status": "pending"
    },
    {
        "id": 7,
        "code": "DELYR5VT9",
        "address": "Ngong",
        "cordinates": [
            -1.363549249007895,
            36.65176391091375
        ],
        "status": "pending"
    },
    {
        "id": 8,
        "code": "DELG589UY",
        "address": "Juja",
        "cordinates": [
            -1.1122958501503692,
            37.00469970188014
        ],
        "status": "pending"
    },
    {
        "id": 18,
        "code": "DELDWRMRu",
        "address": "Kawangware",
        "cordinates": [
            -1.2791143169935622,
            36.74411773170145
        ],
        "status": "pending"
    },
    {
        "id": 19,
        "code": "DEL5TVQ2G",
        "address": "Baba Dogo",
        "cordinates": [
            -1.2476221120245659,
            36.88771247350354
        ],
        "status": "pending"
    },
    {
        "id": 20,
        "code": "DELIN8WHJ",
        "address": "Langata",
        "cordinates": [
            -1.336777509339507,
            36.798706049564714
        ],
        "status": "pending"
    },
    {
        "id": 9,
        "code": "DELDWRMRK",
        "address": "Dagorretti",
        "cordinates": [
            -1.2797149820272347,
            36.74592017615902
        ],
        "status": "pending"
    }
]
```
```source-json
{
    "id": 65,
    "route_path": [
        [
            "Route 0 for vehicle: 0 Load(0) -> Distance of the route: 0milesLoad of the route: 0\n",
            "Route 1 for vehicle: 0 Load(0) -> Distance of the route: 0milesLoad of the route: 0\n",
            "Route 2 for vehicle: 0 Load(0) ->  4 Load(4) ->  1 Load(5) ->  5 Load(9) -> Distance of the route: 30milesLoad of the route: 9\n",
            "Route 3 for vehicle: 0 Load(0) ->  9 Load(8) -> Distance of the route: 6milesLoad of the route: 8\n",
            "Route 4 for vehicle: 0 Load(0) ->  6 Load(4) ->  10 Load(7) ->  7 Load(15) -> Distance of the route: 42milesLoad of the route: 15\n",
            "Route 5 for vehicle: 0 Load(0) ->  8 Load(2) ->  2 Load(10) ->  3 Load(14) -> Distance of the route: 47milesLoad of the route: 14\n"
        ],
        46,
        {
            "total_distance": 125,
            "operations": [
                {
                    "route": 3,
                    "load": 9,
                    "distance": 30,
                    "path": [
                        [
                            -1.2841,
                            36.8155
                        ],
                        [
                            -1.3951257895566065,
                            36.76025390113323
                        ],
                        [
                            -1.4308204984641613,
                            36.6778564402076
                        ],
                        [
                            -1.363549249007895,
                            36.65176391091375
                        ],
                        [
                            -1.2841,
                            36.8155
                        ]
                    ]
                },
                {
                    "route": 4,
                    "load": 8,
                    "distance": 6,
                    "path": [
                        [
                            -1.2841,
                            36.8155
                        ],
                        [
                            -1.336777509339507,
                            36.798706049564714
                        ],
                        [
                            -1.2841,
                            36.8155
                        ]
                    ]
                },
                {
                    "route": 5,
                    "load": 15,
                    "distance": 42,
                    "path": [
                        [
                            -1.2841,
                            36.8155
                        ],
                        [
                            -1.1122958501503692,
                            37.00469970188014
                        ],
                        [
                            -1.2797149820272347,
                            36.74592017615902
                        ],
                        [
                            -1.2791143169935622,
                            36.74411773170145
                        ],
                        [
                            -1.2841,
                            36.8155
                        ]
                    ]
                },
                {
                    "route": 6,
                    "load": 14,
                    "distance": 47,
                    "path": [
                        [
                            -1.2841,
                            36.8155
                        ],
                        [
                            -1.2476221120245659,
                            36.88771247350354
                        ],
                        [
                            -1.1425024035472517,
                            36.964874262432765
                        ],
                        [
                            -1.0271666544093947,
                            37.067871088589584
                        ],
                        [
                            -1.2841,
                            36.8155
                        ]
                    ]
                }
            ]
        }
    ],
    "added": "2023-01-10T19:46:38.729938Z",
    "edited": "2023-01-10T19:46:38.729980Z",
    "vehicle_utilization": "AU",
    "mode": "Minimum Distance",
    "vehicle_capacity": 15,
    "num_vehicles": 8,
    "start_address": "SRID=4326;POINT (36.798107 -1.283922)",
    "end_address": "SRID=4326;POINT (36.798107 -1.283922)"
}
```

https://developers.google.com/maps/documentation/javascript/examples/polyline-simple


## Getting Started
To get started:
 Git clone the repository using https://github.com/EUGINELETHAL/Backend-challenge
 For the API to run smoothly you will need the following:
```
1. Python 3.6 or higher installed.
2. Pip3
3. Pipenv or virtualenv installed.
```
### Installing
> __Local Development Guide.__

1. Git clone the repository using 
2. Through your terminal, navigate to the location with the cloned repository.
3. Open the cloned repo folder using your terminal.
4. You're currently on the `main` branch.



## Running the tests
pytest
### Style Guide.
PEP 8

## Deployment
Heroku


## Built With
* Django and Django Rest Framework

## Authors
* **Ochung Eugine.** 
