# DQA_MONITOR
Is a simple Dash application that broadcasts the [daily QA test](https://github.com/papomail/Daily_QA_UCLH) results, so they can be inspect from the confort of your browser.   



![](/media/DQA_WEB_APP_1.png?raw=true)DQA_MONITOR is currently live at https://uclh.herokuapp.com/   



### Reading the graphs

* The size of the circles is proportional to the standard deviation of the _noise image_.  
A large circle indicates a sub-optimal image substraction, which can be due to **excessive movement** of the liquid inside the phantom.

* The length of the whiskers represent the standar deviation of the SNR measured. Long whiskers indicate a large variation in the SNR across the imaged volume, and that is okay. It is expected that each coil tested will have different SNR variation (as the coil elements can be closer or further away from the source of the signal, depending on the geometry of the test).

*In order to evaluate the performance of rf-coils over time, it is **critical** that every coil is always tested using the same methodology (**same protocol, same FOV, same phantom position, etc**).*


* In an ideal test, a **well performing** coil should appear as a _flat band_ on the graph, with constant NSNR and standar deviation over time.
* In an ideal test, an **under-performing** coil should appear as a _descending slope_, (if the SNR is gradually worsening) or as a _step reduction_ in the event of a sudden loss in SNR.
