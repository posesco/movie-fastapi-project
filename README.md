python3 -m venv venv    

source venv/bin/activate

python3 -m fastapi
python3 -m uvicorn

uvicorn main:app --reload --port 5000 --host 0.0.0.0

docs:

http://milocal.com:5000/docs

http://milocal.com:5000/openapi.json