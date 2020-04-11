# cloud-downloader
Download files directly into the cloud by URL

## Run
### Deploy:  
```bash
virtualenv -p python3 venv
source venv/bin/activate
chmod +x publisher.py consumer.py run_postgres.sh run_rabbitmq.sh
./run_postgres.sh
./run_rabbitmq.sh
./consumer.py
./server.py
```

### Usage:  
Register:  
```bash
curl --location --request POST 'http://localhost:8888/api/register' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "testuser",
    "password": "testpassword"
}'
```
Login:  
```bash
curl --location --request POST 'http://localhost:8888/api/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "testuser",
    "password": "testpassword"
}'
```
Create task:
```bash
curl --location --request POST 'http://localhost:8888/api/download' \
--header 'Content-Type: application/json' \
--data-raw '[
    "http://www.tsu.ru/upload/medialibrary/22d/pobeda75.jpg",
    "http://www.tsu.ru/upload/resize_cache/iblock/4e7/320_213_2/0m8a8521_drugtsu_cam520.jpg"
]'
```
Check status:
```bash
http://localhost:8888/api/status?uuid=2b29a2c7-169a-417c-9bf8-239b1f283cd5
```