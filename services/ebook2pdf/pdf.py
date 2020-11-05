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
URL_CONVERTER_JOBS = app.apps['backend']['epubtopdf']['base_url'] + \
    app.apps['backend']['epubtopdf']['jobs']
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
payload = {'target': 'pdf',
           'category': 'ebook',
           'fail_on_input_error': 'false',
           'fail_on_conversion_error': 'false',
           'process': 'false',
           'csrf_token': '26b6667196c9ee9d5b874247ecd1123c'}
headers_jobs = {
    'cookie': 'OC_PHPSESSID=57j2rgkbs3ub5f3q997t5hsq31; __utmc=77951050; qgExtension=true; qg_consent=true; __utmz=77951050.1602982872.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); lang_hint=en; _pk_ref.1.7d7a=%5B%22%22%2C%22%22%2C1602995363%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.1.7d7a=1; __utma=77951050.98317073.1602566387.1602987141.1602995363.4; __utmt=1; __utmb=77951050.23.10.1602995363; _pk_id.1.7d7a=de170f49efb0ba20.1602566387.4.1602998126.1602987276.; FCCDCF=[["AKsRol_Iy64za6j1Be3s3JNzON92XzExGLfYotsLUwNl-h7nuVj_Tf3lREkf7uvykXDtXOrkMeT1X2pfWt2oDLmKnd_jYLlwdrG5_k1FK3oP7RnLQO1ZsbX4ZVmrvcBybwWl0guafhTWQsaPWl5xDuoiMR8-mew41Q=="],null,["[[],[],[],[],null,null,true]",1602998127406]]; OC_PHPSESSID=90nov7us6r1jcvm8pu0rq6vq4d'
}


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
        _req_job = requests.request(
            "POST", URL_CONVERTER_JOBS, headers=headers_jobs, data=payload, files=[])
        """Prepare the payload for the request"""
        _req_job_json = _req_job.json()
        """Get upload url"""
        upload_url = _req_job_json['upload_url']
        """Define headers"""
        headers_upload = {
            'x-oc-upload-uuid': 'd6063f3a-fd42-e380-890f-8bd9dbb72012',
            'x-oc-token': _req_job_json['token'],
            'Cookie': 'OC_PHPSESSID=90nov7us6r1jcvm8pu0rq6vq4d'
        }
        payload_upload = {'csrf_tokern': '26b6667196c9ee9d5b874247ecd1123c'}
        files_upload = [
            ('file', _file)
        ]
        """Post request to app converter"""
        req_enqueue = requests.request(
            "POST", upload_url, data=payload_upload, headers=headers_upload, files=files_upload)
        """Check if it has any problem"""
        if req_enqueue.status_code != 200:
            continue
        url_start = "{0}/{1}/start".format(URL_CONVERTER_JOBS,
                                           _req_job_json['id'])
        """Prepare activate url"""
        payload_start = {'target': 'pdf',
                         'category': 'ebook',
                         'reader': 'default',
                         'string_method': 'convert-to-pdf',
                         'conversion_id': _req_job_json['conversion'][-1]['id'],
                         'title': '',
                         'author': '',
                         'border': '',
                         'base_font_size': '',
                         'embed_font': '',
                         'encoding': '',
                         'csrf_token': '26b6667196c9ee9d5b874247ecd1123c'}
        headers_start = {
            'Referer': 'https://ebook.online-convert.com/convert-to-pdf',
            'Origin': 'https://ebook.online-convert.com',
            'Cookie': 'OC_PHPSESSID=57j2rgkbs3ub5f3q997t5hsq31; __utmc=77951050; qgExtension=true; qg_consent=true; __utmz=77951050.1602982872.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); lang_hint=en; _pk_ref.1.7d7a=%5B%22%22%2C%22%22%2C1602995363%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.1.7d7a=1; __utma=77951050.98317073.1602566387.1602987141.1602995363.4; __utmb=77951050.23.10.1602995363; _pk_id.1.7d7a=de170f49efb0ba20.1602566387.4.1602998126.1602987276.; FCCDCF=[["AKsRol_Iy64za6j1Be3s3JNzON92XzExGLfYotsLUwNl-h7nuVj_Tf3lREkf7uvykXDtXOrkMeT1X2pfWt2oDLmKnd_jYLlwdrG5_k1FK3oP7RnLQO1ZsbX4ZVmrvcBybwWl0guafhTWQsaPWl5xDuoiMR8-mew41Q=="],null,["[[],[],[],[],null,null,true]",1602998127406]]; OC_PHPSESSID=90nov7us6r1jcvm8pu0rq6vq4d',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'accept-language': 'es-ES,es;q=0.9,en;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept': 'application/json, text/javascript, */*; q=0.01'
        }

        req_start = requests.request(
            "POST", url_start, data=payload_start, headers=headers_start, files=[])
        """Check if it has any problem"""
        if req_start.status_code != 200:
            continue
        """Callback"""
        url_status = "{0}/{1}/callbackstatus".format(
            URL_CONVERTER_JOBS, _req_job_json['id'])
        """Request to activate the process"""
        """Get the content from the response"""
        for i in range(0, PDF_MAX_DOWNLOAD_RETRY):
            """Sleep 3 seconds"""
            sleep(PDF_SLEEP_DOWNLOAD_TIME)
            """Download from the url"""
            req_download = requests.request("GET", url_status)
            """Check if the response has any problem"""
            if req_download.status_code != 200:
                break
            req_download_json = req_download.json()
            if req_download_json['status'] != 'completed':
                continue
            else:
                """Exit from the loop"""
                _output = req_download_json['output'][-1]
                break
        """Check if it has any problem"""
        if not _output:
            continue
        _process_id = _req_job_json['id']
        req_content = requests.request("GET", _output['uri'])
        """Define out filename"""
        _out_fname = "{0}/{1}.pdf".format(
            PDF_OUT_PATH,
            _process_id
        )
        _content=req_content.content
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
        rmfile(_out_fname)
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
