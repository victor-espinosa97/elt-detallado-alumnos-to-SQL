
python3 -m pip install -r requirements.txt

Ejectuar:
````
uvicorn main:app --reload
````

subir un archivo de excel al endpoint:

````
http://localhost:8000/cargar-estudiantes/
````