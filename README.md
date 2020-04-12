# cloud-downloader
:rocket: Download files directly into the cloud with a list of URLs (RabbitMQ, PostgreSQL, Tornado Web Server)

## Note
:construction: Work in progress. Early PoC. 

## Run
### Deploy  
Run with 5 downloader instances:
```bash
docker-compose up --scale cloud-downloader-consumer=5
```
And wait until the consumer and server will connect to RabbitMQ and PostgreSQL (about 10-20 seconds, you will see tracebacks and errors during this time - it's okay for now :smile:).

### Usage  
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
}' -c cookies.txt
```
Create task:
```bash
curl --location --request POST 'http://localhost:8888/api/download' \
--header 'Content-Type: application/json' \
--data-raw '[
    "http://www.tsu.ru/upload/medialibrary/22d/pobeda75.jpg",
    "http://www.tsu.ru/upload/resize_cache/iblock/4e7/320_213_2/0m8a8521_drugtsu_cam520.jpg"
]' -b cookies.txt
```
Check status:
```bash
http://localhost:8888/api/status?uuid=2b29a2c7-169a-417c-9bf8-239b1f283cd5
```
or  
```bash
curl --location --request GET 'http://localhost:8888/api/status?uuid=4ae0f42d-552d-46ea-8358-6938a40aa8fe' -b cookies.txt
```
If status is "ok/done", you can check downloaded files in `data/{UUID}` directory.
