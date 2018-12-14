from app import initialize_app
application = initialize_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
