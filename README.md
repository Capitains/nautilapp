Nautilapp
=========

NautilApp provide a Graphical User Interface (GUI) that helps you run your own Nautilus and Nemo API, two web servers that allows you to browse your own corpora and the corpora from established projects such as the Perseus Digital Library. 

It provides a basic interface such as the one available at http://cts.perseids.org

![Screenshot](images/screenshot.png)


## Download

Download the matching binaries and have fun!

- [NautilApp for Windows](https://github.com/Capitains/nautilapp/raw/master/dist/NautilusApp.exe)
- [NautilApp for Mac](https://github.com/Capitains/nautilapp/raw/master/dist/NautilusAppMac)
- [NautilApp for Ubuntu](https://github.com/Capitains/nautilapp/raw/master/dist/NautilusAppUbuntu)

## How to use

1. First, download the application for your own environment
2. Download at least one corpus (Example : [Perseus Canonical Latin Literature](https://github.com/PerseusDL/canonical-latinLit/archive/master.zip)), unzip it#
3. Open the Application
4. ![Click on load a directory](images/step1.png)
5. ![Select the directory containing the corpus, it should have a data subfolder](images/step2.png)
6. ![Click on run server](images/step3.png)
7. ![Open the server](images/step4.png)
    1. [Go to http://localhost:5000 if you want to browse the text in the raw reading environment](http://localhost:5000)
    2. [Go to http://localhost:5000/api/cts if you want to browse the text in the CTS API](http://localhost:5000/api/cts)

## Developers

The GUI has been quickly developed and I am not a really good and efficient GUI designer. This repository is pretty much open to any PR that would make the following better : 

1. Add more option on how to run the application (Choose the IP to run on, choose the Port to run on)
2. Fix bugs that I would have missed
3. Enhance the GUI that is really crappy (While keeping the same functions and not have to worry about that)
4. Provide an automatic cross-system builer through Travis or the likes
