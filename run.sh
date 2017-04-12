#! /bin/bash
echo "starting redis"
redis-server &
echo "starting mongodb ..."
mongod --quiet &
echo "mongodb started, loading data..."
sleep 1;
cd /root/Conformance_Backend
python load_test_type.py
mongoimport -d fhirtest -c TestData --file TestCases --type json

echo "data loaded, starting server..."
export C_FORCE_ROOT=true
python listener/fhir_flask.py &
python -m task_runner &
celery -A task_runner.tasks worker &
node-supervisor ./bin/www