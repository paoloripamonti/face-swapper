from app import app

if __name__ == '__main__':

    print("Start up project: %s" % app.name)
    app.run(host='127.0.0.1', port=8080, debug=True)
