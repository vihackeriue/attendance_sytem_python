from app import create_app, start_scheduler

app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
