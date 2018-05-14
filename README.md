Item catalog allows you to catalog items for different sports.

to get started

1 for easy setup clone this repo
$ git clone https://github.com/udacity/fullstack-nanodegree-vm

2 cd to $ cd fullstack-nanodegree-vm repo

3 cd to vagrant directory $ cd vagrant

4 start up vm $ vagrant up

5 ssh into vm $ vagrant ssh

6 change directorys to vagrant $ cd vagrant

7 clone this repo within the vagrant directory
https://github.com/zach-col/itemCatalog.git

8 change directorys to the downloaded repo

9 run the command python database_setup.py this will setup the database

10 add data to the database by running the command python lotsOfCatalogs.py

11 go to google console developer and create an API key with credential
https://console.developers.google.com/apis/credentials

12 add this as authorized origins
http://localhost:8000

13 add this as authorized redirects
http://localhost:2200/disconnect
http://localhost:8000/catalogs
http://localhost:8000/gconnect

14 download the clients_secrets json file on google

15 replace this file in client_secrets.json with your json file from google

16 add your client id on line 18 in the file templates/googleSignIn.html

17 to run the application run the command python application.py

18 open a browser and go to localhost:5000
