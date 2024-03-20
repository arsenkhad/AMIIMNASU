# AMIIMNASU
This is a repository dedicated to "analytical models and system level simulation" course in BMSTU (Bauman Moscow State Technical University).

## Getting started
* Install packages listed in `requirements.txt`.
* Update `tex_init.py` with relevant information (for students).
* Enter your input to input files in task folders (check info below).
* Run `main.py` to generate latex reports for all works or run any `task?.py` files in `dz?` folders individually to get a direct terminal output for any individual task.

Below will be placed and updated information about all tasks individually.

# Tasks
## Homework 1
Located in folder `dz1` and dedicated to Markov chains processing.

### Task1
Modeling and processing of Markov chains, set by transition matrix.

#### Input
Input filename is `input_task1.txt` by default, but can be set when launching `task1.py` individually.

Input contains following parts:
* Variant number (optional, required for students)
* Matrix NxN
#### Input example
```
74				
0.19    0.17	0.23	0.21	0.2
0.23	0.15	0.21	0.17	0.24
0.23	0.25	0.25	0.17	0.1
0.16	0.25	0.18	0.22	0.19
0.16	0.23	0.25	0.22	0.14
```
