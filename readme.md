# Flask Demo


### Installation

1. Clone repo.
2. pip install virtualenvwrapper
3. copy the following into User's .bashrc file:<br>
export WORKON_HOME=~/Envs<br>
mkdir -p $WORKON_HOME<br>
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3.4<br>
source /usr/local/bin/virtualenvwrapper.sh<br>
4. Make a virtual environment for the app $mkvirtualenv demo
5. Navigate to the project route and $pip install -r requirements.txt
6. Run tests with $python manage.py test
7. Run development server with $python manage.py runserver


### Application configurations
- Development
    - The default configuration. Uses the development database and pretty printed JSON
    by default.
    - To enable minified json set the environment variable MINIFY_JSON=true.
- Testing
    - Used when testing by default. Uses a testing database that has all tables dropped after every test.
- Production
    - A simulated production configuration. Uses the production database and compact JSON.
    - Enable by setting the environment variable FLASK_CONFIG=production
 
### Database Migrations
- First initialize the migrations folder: $python manage.py db init
- Generate the migration script: $python manage.py db migrate
- After inspecting the generated migration script: $python manage.py db upgrade

### Testing
- Running tests is straightforward: $python manage.py test
- To include coverage (with generated html): $python manage.py test --coverage

### Admin Tools
- Flask-Admin views are available at BASE_URL/admin/group
- While models can not be created, existing models can be updated and Users added or
removed from Groups

## Endpoints

#### api/users
    GET - Returns a list of all Users ordered alphabetically.
    POST params: name (required), email (required) - Creates a new user. Email must be unique
     
#### api/users/group_counts
    GET - Returns a list of all Users ordered by the number of groups they are members of.

#### api/users/<int:id>
    GET - Returns a User including a listing of the User's group memberships (id only)
    DELETE - Deletes a User.
    PUT params: name(required), email (required) - Updates an existing user.

#### api/users/<int:id>/groups
    GET - Returns a list of the Users's Group memberships.
    PUT params: group_id (required) - Adds the User to the specified Group.
    DELETE params: group_id (required) - Removes the User from the specified Group.
    
#### api/groups
    GET - List all Groups ordered alphabetically
    POST params: name (required), description (optional) - Creates a Group. Name must be unique

#### api/groups/user_counts
    GET - Returns a list of all Groups sorted by the number of members (ascending)

#### api/groups/<int:id>
    GET - Returns a Group including a listing of the Group's users (id only)
    DELETE - Deletes a Group (will not delete Users that are members)
    PUT params: name (required), description (optional) - Updates a Group. Name must be unique.
    
#### api/groups/<int:id>/users
    GET - Returns a list of a Group's users.