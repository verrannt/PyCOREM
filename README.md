# PyCOREM
The pycorem object supplies some useful functions for interacting with the [COREM library for Retina modelling](https://github.com/pablomc88/COREM). It depends on **Numpy**. Please be aware that you should be a little bit familiar with COREM (Check the wiki [here](https://github.com/pablomc88/COREM/wiki)) before using it.

To use this object, simply copy the pycorem.py file into the directory you are working from. In your file, define the path to the main COREM library and initialize a new PyCOREM object for this directory:
```python
path_corem = "/home/pscl/Documents/Uni/CompNeuroScience/COREM-master/COREM/"
pc = Pycorem(path_corem)
```

PyCOREM offers the following functions:

###### generate_script(hyper_params, retina_params, name)
Generate a script file for COREM with specific hyperparameters and parameters for the cells and a name. The script will be saved in the main COREM directory under Retina_scripts/name. You have to specify the hyper parameters (as dict) and retina parameters (as array), or simply use the ones provided by PyCOREM, which are:
```python
self.hyper_params = {
    "sim_time" : "185",
    "multim_start" : "100",
    "multim_mode" : "temporal",
    "multim_show" : "False",
    "cell_x" : "10",
    "cell_y" : "10",
    "input" : "retina.Input('impulse'{'start','100.0','stop','120.0','amplitude','200.0','offset','0.0','sizeX','20','sizeY','20'})"
}

self.retina_params = [
    23.1, # tau_photoreceptor
    2.95, # tau_horizontal
    3.3,  # tau_off_bipolar
    8.0,  # tau_on_bipolar
    -0.0055, # slope_photoreceptor
    0.994,   # slope_horizontal
    15.08,   # slope_off_bipolar
    -22.73   # slope_on_bipolar
]  
```

###### call_script(name, show)
Call a Retina script of a specific name. if *show* == False, COREM will be kept from printing to the console (defaults to True).

###### read_results(ids, n)
Read the results from the COREM/results directory of the different cells specified in *ids*. You have to specify the number of the cell *n* if the multimeter was configured to measure all cells instead of just one.

###### get_eccentricity_function(cell, degree)
This simply returns the eccentricity function used to scale the output of a specific cell with eccentricity on the retina. 

### Example
```python
import matplotlib.pyplot as plt
import numpy as np
from pycorem import Pycorem

path_corem = "/home/pscl/Documents/Uni/CompNeuroScience/COREM-master/COREM/"
pc = Pycorem(path_corem)

pc.generate_script(pc.hyper_params, pc.retina_params, name="script.corem")
pc.call_script("script.corem", show=True)

ids = ['SNL_photoreceptor', 'SNL_OFF_bipolar', 'SNL_ON_bipolar']
results = pc.read_results(ids)
photor = results[0]
off_bip = results[1]
on_bip = results[2]

degree = 15
ecc1 = pc.get_eccentricity_function("photoreceptor", degree)
ecc2 = pc.get_eccentricity_function("off_bipolar", degree)
ecc3 = pc.get_eccentricity_function("on_bipolar", degree)

# Plot model at specific degree of eccentricity
model = ecc1 * photor + ecc2 * off_bip + ecc3 * on_bip
plt.plot(np.arange(len(model)), model)
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude (mV)")
plt.show()

```
