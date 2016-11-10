About
=====

Implementation of [Neural Programmer-Interpreters](http://arxiv.org/abs/1511.06279) with Keras.

based on mokemokechicken work.

multiplication task work in progress

How to Demo
===========

[Demo Movie](https://youtu.be/s7PuBqwI2YA)

requirement
-----------

* Python3

setup
-----

```
pip install -r requirements.txt
```
##  Task: addition

create training dataset(addition)
-----------------------
### create training dataset
```
sh src/run_create_addition_data.sh
```

### create training dataset with showing steps on terminal
```
DEBUG=1 sh src/run_create_addition_data.sh
```



raining model(addition)
------------------
### Create New Model (-> remove old model if exists and then create new model)
```
NEW_MODEL=1 sh src/run_train_addition_model.sh
```

### Training Existing Model (-> if a model exists, use the model)
```
sh src/run_train_addition_model.sh
```



test model(addition)
----------
### check the model accuracy
```
sh src/run_test_addition_model.sh
```

### check the model accuracy with showing steps on terminal
```
DEBUG=1 sh src/run_test_addition_model.sh
```

##  Task: multiplication

create training dataset(multiplication)
-----------------------
### create training dataset(up to two digits, it takes a few mins to generate all the data, be patient)
```
sh src/run_create_multiplication_data.sh
```

### create training dataset with showing steps on terminal
```
DEBUG=1 sh src/run_create_multiplication_data.sh
```


training model(multiplication)
------------------
### Create New Model (-> remove old model if exists and then create new model)
```
NEW_MODEL=1 sh src/run_train_multiplication_model.sh
```

### Training Existing Model (-> if a model exists, use the model)
```
sh src/run_train_multiplication_model.sh
```
