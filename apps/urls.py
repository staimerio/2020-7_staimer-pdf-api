# Retic
from retic import App as app

"""Define all other apps"""
BACKEND_ONLINE_CONVERTER = {
    u"base_url": app.config.get('APP_BACKEND_ONLINE_CONVERTER'),
    u"get_host": "/get/host",
}
BACKEND_EBOOK_ONLINE_CONVERTER = {
    u"base_url": app.config.get('APP_BACKEND_EBOOK_ONLINE_CONVERTER'),
    u"jobs": "/jobs",
}

APP_BACKEND = {
    u"converter": BACKEND_ONLINE_CONVERTER,
    u"epubtopdf": BACKEND_EBOOK_ONLINE_CONVERTER
}

"""Add Backend apps"""
app.use(APP_BACKEND, "backend")
