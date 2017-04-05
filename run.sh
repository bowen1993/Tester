#! /bin/bash
echo "starting redis"
redis-server &
echo "starting mongodb ..."
mongod --quiet &
echo "mongodb started, loading data..."
cd /root/Conformance_Backend
mongoimport -d fhirtest -c TestData --file TestCases --type json
python load_test_type.py

echo "data loaded, starting server..."
export C_FORCE_ROOT=true
python -m task_runner &
celery -A task_runner.tasks worker &
npm start