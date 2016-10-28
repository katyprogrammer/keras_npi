#!/bin/sh

THIS_DIR=$(cd $(dirname $0); pwd)
DATA_DIR=${THIS_DIR}/../data/multiplication
MODEL_OUTPUT=${1:-${DATA_DIR}/multiplication.model}
NUM_TEST=${2:-100}

export PYTHONPATH=${THIS_DIR}
cd "$THIS_DIR"

mkdir -p "$DATA_DIR"

echo python npi/multiply/test_model.py "$MODEL_OUTPUT" "$NUM_TEST"
python npi/multiply/test_model.py "$MODEL_OUTPUT" "$NUM_TEST"
