"""Entry point to the application"""

from application import create_app
import os

app = create_app()

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 8000)

    app.run(host="0.0.0.0", port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
