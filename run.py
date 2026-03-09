from app import create_app, create_default_admin

app = create_app()

with app.app_context():
    create_default_admin()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

