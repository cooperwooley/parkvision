from flask_sqlalchemy import SQLAlchemy
from . import create_app

app = create_app()

db = SQLALchemy(app)

if __name__ == '__main__':
    app.run(debug=True)