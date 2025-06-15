cd ..
cd extract
docker build -t aisprid-extract .

cd ..
cd load
docker build -t aisprid-load .

cd ..
cd transform
docker build -t aisprid-transform .

cd ..
cd worker
docker build -t aisprid-worker .