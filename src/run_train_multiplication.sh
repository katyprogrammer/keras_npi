#!/bin/sh

THIS_DIR=$(cd $(dirname $0); pwd)
DATA_DIR=${THIS_DIR}/../data/multiplication
TRAIN_DATA=${1:-${DATA_DIR}/train.pkl}
MODEL_OUTPUT=${2:-${DATA_DIR}/multiplication.model}

export PYTHONPATH=${THIS_DIR}
cd "$THIS_DIR"

mkdir -p "$DATA_DIR"

[ "$NEW_MODEL" != "" ] && rm -f "$MODEL_OUTPUT"

echo python npi/multiply/training_model.py "$TRAIN_DATA" "$MODEL_OUTPUT"
time python npi/multiply/training_model.py "$TRAIN_DATA" "$MODEL_OUTPUT"
