# LGS Metadata Table Builder

### Version 1.0

This module is designed to build the LGS metadata table using all available epochs, either by importing the existing fits file if it exists and checking which epochs need to be appended, or generating a brand new file if it does not.  It also creates a backup folder to save the previous builds.

## Getting Started

### Prerequisites

This module is designed to be completely self contained and devoid of any proprietary dependencies.  However, in order to ensure that the most recent epochs are included, use the following rsync block in terminal to download any new data:

```
rsync -av --include="*lgs" --include="*lgs/clean" --include="*lgs/clean/*" --include="*lgs/clean/*/*" --include="*lgs/combo" --include="*lgs/combo/*" --include="*lgs/combo/*/*" --include="*lgs*" --include="*lgs*/clean" --include="*lgs*/clean/*" --include="*lgs*/clean/*/*" --include="*lgs*/combo" --include="*lgs*/combo/*" --include="*lgs*/combo/*/*" --exclude="*" USER@nyx.astro.ucla.edu:/g/ghez/data/gc/ /g/lu/data/gc/lgs_data
```

### Installing

Download lgs_metadata_compiler.py, put in the current working directory.


## Use

In it's current iteration, the module is intended to be imported and the update() function called.

```
import lgs_metadata_compiler as lmc
lmc.update()
```

Future version could run from terminal and take user inputs for options such as verbose mode.


## Author

* **Steve Robinson** - *Initial work* 

## Acknowledgments

* Many of the functions for collecting seeing and CFHT data were modified from code created by Jessica Lu