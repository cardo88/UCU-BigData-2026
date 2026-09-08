# levantar los contenedores
docker compose up -d

# ver que estén corriendo
docker compose ps

# conectarse por psql desde la terminal
docker exec -it bigdata-postgres psql -U bigdata -d bigdata_db

# apagar (mantiene los datos en el volumen)
docker compose down

# apagar y borrar todo, incluidos los datos
docker compose down -v