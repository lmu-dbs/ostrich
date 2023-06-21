# Prototypical Implementation of OSTRICH

[![Python 3.10](https://img.shields.io/badge/Python-3.10-2d618c?logo=python)](https://docs.python.org/3.10/)

This repository consists of the prototypical implementation of the following paper:

***OSTRICH: Ordering Subtraces Regarding Temporal Characteristic* by Janina Sontheim, Ludwig Zellner, Simon Rauch, and Thomas Seidl**

### Preconditions
* A database consisting of sequences and corresponding timestamps is required
* You have to convert your sequences and your timestamp data into [IBMGenerator format](https://www.philippe-fournier-viger.com/spmf/Converting_a_sequence_database_to_SPMF.php)
* For reference have a look at the example given in the folder `data`

### Usage
1. Run `main.py` with support and confidence thresholds of your choice
2. Copy the resulting rule-file into the folder data
3. Run `preprocessor.py` (adapt paths if required)
4. Run `subcluster.py` with adapted minimum epsilon and minimum amount of samples
