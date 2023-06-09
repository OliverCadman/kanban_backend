"""Entry point to the application"""

from application import create_app
import os

app = create_app()


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 8000)

    context = ("./server.crt", "./server.key")
    app.run(host="0.0.0.0", port=443, debug=ENVIRONMENT_DEBUG, ssl_context=context)
