# Flaskサーバーを起動するときに使う
from flmapp import create_app

app = create_app()

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True, threaded=True,port=5000)