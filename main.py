# Main bestand: hier wordt de app gecreëerd en gerund.

from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run()