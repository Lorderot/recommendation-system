from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from server import app, db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

# python manage.py db migrate //detects changes
# python manage.py db upgrade //updates DB

if __name__ == '__main__':
    manager.run()
