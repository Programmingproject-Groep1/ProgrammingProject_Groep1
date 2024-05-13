# Main bestand: hier wordt de app gecreëerd en gerund.

from website import create_app
from flask_dropzone import Dropzone

app = create_app()

app.config.update(
    DROPZONE_ALLOWED_FILE_TYPE='image',
    DROPZONE_MAX_FILE_SIZE=3,
    DROPZONE_MAX_FILES=30,
    DROPZONE_IN_FORM=True,
    DROPZONE_UPLOAD_ON_CLICK=True,
    DROPZONE_UPLOAD_ACTION='/',
    DROPZONE_UPLOAD_BTN_ID='submit',
)

dropzone = Dropzone(app)


if __name__ == '__main__':
    app.run(debug=True)
