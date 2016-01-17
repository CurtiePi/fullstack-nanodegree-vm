Place your catalog project in this directory.
Catalog project

This project covers the following:
Building a webserver
Creating a Database
Performing CRUD operations on database
Oauth authentication

How to run this project:

Step 1: Clone the repository

$  git clone https://github.com/CurtiePi/fullstack-nanodegree-vm.git catalog

Note this will clone a number of projects along with the catlog project
if you only want to have the catalog project related files then:

Step 1b: 

$ cd  catalog
$ git filer-brance --prune-empty --subdirectory-filter vagrant/catalog HEAD

NOTE if you do not perform Step 1b then you must 
$ cd catalog/vagrant/catalog

to get to the files needed for this project
The structure of this project is as follows
catalog
|
- database_setup.py
- client_secrets.json
- createsportinggoods.py
- fb_client_secrets.json
- project.py
|
--|
  - static
  |      |
  |      - styles.css
  |      |
  |      |
  |      - images
  |             |
  |             - default
  |             |
  |             - NoPicAvailable.png
  |
  |
  - templates
         |
         - categories.html
         - deleteequipment.html
         - editequipment.html
         - equipment.html
         - equipmentdetail.html
         - header.html
         - latestequipment.html
         - login.html
         - newequipment.html

Step 2: Set up your database

The database has 3 tables:

User
- id      integer
- name    string
- picture string
- email   string

Category
- id      integer
- name    string

Equipment
- id      integer
- name    string
- price   string
- image   string
- description string
- entry_time  datetime
- catergory_id integer foreign key Category.id

To create the database run
$ python database_setup.py

this will create the database sportinggoods.db

Step 3: Populate the database

$ python createsportinggoods.py


Step 4: Start the application

$ python project.py

Step 5: Using the application
How it works (hopefully):

The main screen should have two parts:
1. Categories
2. Equipment listing

The first listing is equipment recently added to the database, currently set at anyting 
added less than 16 hours from the current time.

Clicking on a category will list all the euipment in that category, 

Clicking on the equipmnt will take you to a detailed description page.

None of the above screens allows the user to edit, or add information. In order
to edit, delete or create new equipment entries the user must log in.

Logging in utilizes both facebook and google authentication.

Once a user is authenticated via google or facebook the my create equipment from the 
Category Equipment listing page - equipment.html

The user may delete or edit equipment from:
Equipment Detail page - equipmentdetail.html
Category Equipment listing page - equipment.html

When they user logs in the session is populated with user information which can be used
later. When the user disconnects, the session data is cleared.

Note when a user edits, adds equipment if no image is assigned the equipment will be given
a default image. Also the application will create category specific directories to hold the 
images for equipment in that category. Uploading a new image will remove the old image and 
deleting the equipment will remove its related image unless it's a default image.

Step 6: Stopping the application
$ Ctrl-C


Some private notes:
1. Working from behind the GFW is really a detriment
2. Coule use more CSS styling
3. More time I would create user roles so that only certain users could add and/or delete
