"""Servicios para el controlador de archivos"""

# Retic
from retic import env, App as app

# Requests
import requests

# Os
import os

# Binascii
import binascii

# Services
from retic.services.general.urls import slugify
from retic.services.general.time import sleep
from retic.services.responses import success_response_service, error_response_service

# Utils
from services.general.general import rmfile

# Constants
URL_CONVERTER_HOST = app.apps['backend']['converter']['base_url'] + \
    app.apps['backend']['converter']['get_host']
BODY_POST_REQ = {
    "class": "ebook",
    "from": "epub",
    "to": "pdf",
    "source": "file",
}
PDF_SLEEP_DOWNLOAD_TIME = app.config.get(
    'PDF_SLEEP_DOWNLOAD_TIME', callback=int)
PDF_OUT_PATH = app.config.get('PDF_OUT_PATH')
PDF_MAX_DOWNLOAD_RETRY = app.config.get('PDF_MAX_DOWNLOAD_RETRY', callback=int)


def build_from_epub_list(files, binary_response=False):
    """Build a pdf file from epub file

    :param files: List of Epub file to convert to pdf format
    :param binary_response: Flag that assign if the response will has a binary file
    """
    """Define all variables"""
    _pdf_files = []
    """For each file do to the following"""
    for _file in files:
        _content = None
        """Get host from app converter"""
        _req_host = requests.get(URL_CONVERTER_HOST)
        """Prepare the payload for the request"""
        _files = {'file': _file}
        """Post request to app converter"""
        req_enqueue = requests.post(
            _req_host.text,
            data=BODY_POST_REQ,
            files=_files
        )
        """Check if it has any problem"""
        if req_enqueue.status_code != 200:
            continue
        """Prepare activate url"""
        _activate_url = req_enqueue.text.replace("\x00", "")
        """Request to activate the process"""
        req_activate = requests.get(_activate_url)
        """Get id of the process"""
        _process_id = _activate_url.split("/convert/")[-1]
        """Prepare download url"""
        _download_url = _req_host.text.replace(
            "/send", "/{}/download".format(_process_id)
        )
        """Get the content from the response"""
        for i in range(0, PDF_MAX_DOWNLOAD_RETRY):
            """Sleep 3 seconds"""
            sleep(PDF_SLEEP_DOWNLOAD_TIME)
            """Download from the url"""
            req_download = requests.get(_download_url)
            """Check if the response has any problem"""
            if req_download.status_code != 200:
                continue
            else:
                """Exit from the loop"""
                _content = req_download.content
                break
        """Check if it has any problem"""
        if not _content:
            continue
        """Define out filename"""
        _out_fname = "{0}/{1}.pdf".format(
            PDF_OUT_PATH,
            _process_id
        )
        """Write the file"""
        open(_out_fname, 'wb').write(_content)
        """Get size of file"""
        _size = os.path.getsize(_out_fname)
        """Check if binary response is True"""
        if binary_response == "True":
            """Get content from the file"""
            _data_b64 = binascii.b2a_base64(
                _content
            ).decode('utf-8')
        else:
            _data_b64 = None
        """Delete file"""
        # rmfile(_out_fname)
        """Transform name"""
        if _file.filename:
            _filename = _file.filename
        else:
            _filename = _process_id
        """Transform data response"""
        _pdf = {
            u"title": _filename,
            u"pdf_title": slugify(_filename)+".pdf",
            u"pdf_size": _size,
            u"pdf_id": _process_id,
            u"pdf_b64": _data_b64
        }
        """Add file to list"""
        _pdf_files.append({
            u"pdf": _pdf
        })
    """Return the data"""
    return success_response_service(
        data=_pdf_files
    )
