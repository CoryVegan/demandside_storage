# Demand-side Storage Model

### Purpose
The purpose of this model is to determine whether it is currently economically justified to purchase batteries for home electricity storage in order to take advantage of time-of-use pricing.

More info available at http://www.thetrainingset.com/articles/Intro-To-Storage-Model/

Modeling largely relies on Pandas to handle time series.

### Data Sources

Green button sample data: http://www.thetrainingset.com/articles/Feeding-The-Data-Monster/

BGE time-of-use electricity pricing plans: http://www.thetrainingset.com/articles/BGE-Pricing/

### Modules

See docstrings in each module for details and usage.

* TOU_pricing.py: Determines assigns peak, intermediate, and off-peak periods 

* storage_logic.py: Contains the logic for the model.  Calculates hourly states for an entire year based on demand, cost of electricity, and storage capacity.

* parameters.py: If only simulating for one set of parameters, this file can be used.  Otherwise, analysis is conducted in analysis.ipynb where certain parameters can be varied to assess their impact on the system performance.

* calculations.py: Once the hourly states are determined for a year, the functions in this module return salient metrics of the system performance.

### Notebooks

* analysis.ipynb: This is where I actually examine the behavior of the model and determine the effects of the model parameters.
