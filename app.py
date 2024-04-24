from flask import Flask
from index import index_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(index_bp)

if __name__ == '__main__':
    app.run(debug=True)
