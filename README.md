to run the project make sure to have following modules installed:
Rserve (pip install Rserve)
PYQT5 (pip install PYQT5)
R (download from offical webpage https://www.r-project.org/)
R tools (download from official webpage https://www.r-project.org/)

to run the R with Rserve:
install package Rserve in the R gui or R studio
run following commands:
library(Rserve)
Rserve(args="--vanilla --RS-port 6312") # change the port as you wish 
