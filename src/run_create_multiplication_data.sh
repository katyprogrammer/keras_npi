#!/bin/sh

THIS_DIR=$(cd $(dirname $0); pwd)
DATA_DIR=${THIS_DIR}/../data/multiplication
OUTPUT_FILE=${1:-${DATA_DIR}/train_up_to_two_digits.pkl}
LOG=train_result_up_to_two_digits.log
export PYTHONPATH=${THIS_DIR}
cd $THIS_DIR

mkdir -p "$DATA_DIR"

rm -f "$LOG"
echo python npi/multiply/create_training_data.py "$OUTPUT_FILE" 1000 "$LOG"
python npi/multiply/create_training_data.py "$OUTPUT_FILE" 1000 "$LOG"
