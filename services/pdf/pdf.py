"""Servicios para el controlador de archivos"""

# Retic
from retic import env, App as app

# Requests
import requests

# Os
import os

# Uuid
import uuid

# Binascii
import binascii

# Xhtml2pdf
from xhtml2pdf import pisa             # import python module

# Pypdf4
from PyPDF4 import PdfFileWriter, PdfFileReader

# Img2pdf
import img2pdf

# Services
from retic.services.general.time import sleep
from retic.services.responses import success_response_service, error_response_service

# Utils
from services.general.general import rmfile, slugify

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
PDF_FONT_PATH = app.config.get('PDF_FONT_PATH')
PDF_MAX_DOWNLOAD_RETRY = app.config.get('PDF_MAX_DOWNLOAD_RETRY', callback=int)

PDF_CSS_BASE = '''@namespace epub "http://www.idpf.org/2007/ops";'''

PDF_CSS_STYLE_RUSSIAN = PDF_CSS_BASE+'''p, h1, h2 {font-family: "Roboto", sans-serif !important;}h2 {text-align:left;text-transform:uppercase;font-weight:200}ol {list-style-type:none}ol>li:first-child{margin-top:.3em}nav[epub|type~=toc]>ol>li>ol {list-style-type:square}nav[epub|type~=toc]>ol>li>ol>li {margin-top:.3em}p {font-size: 1.8rem;}h1 {text-transform: uppercase;font-size: 3rem;}a {padding: 3px 3px;font-weight: bold;text-transform: uppercase;color: #272727;border-radius: 7px;font-size: 2rem;}h2 {margin: 0px 0px 0px 0px;font-size: 2.5rem; text-transform: uppercase !important;text-align:center} @font-face {font-family: Roboto; src: url("''' + \
    PDF_FONT_PATH + \
    '''/Roboto-Regular.ttf");} @font-face {font-family: Roboto; src: url("''' + \
    PDF_FONT_PATH + \
    '''/Roboto-Bold.ttf"); font-weight: bold;}'''

PDF_CSS_STYLE_CHINESE = PDF_CSS_BASE+'''p, h1, h2 {padding-right: 100px !important; padding-left: 100px !important;margin-right: 100px !important; margin-left: 100px !important; font-family: "HanyiSentyCandy" !important;}h2 {text-align:left;text-transform:uppercase;font-weight:200}ol {list-style-type:none}ol>li:first-child{margin-top:.3em}nav[epub|type~=toc]>ol>li>ol {list-style-type:square}nav[epub|type~=toc]>ol>li>ol>li {margin-top:.3em}p {font-size: 1.8rem;}h1 {text-transform: uppercase;font-size: 3rem;}a {padding: 3px 3px;font-weight: bold;text-transform: uppercase;color: #272727;border-radius: 7px;font-size: 2rem;}h2 {font-size: 2.5rem; text-transform: uppercase !important;text-align:center} @font-face {font-family: HanyiSentyCandy; src: url("''' + \
    PDF_FONT_PATH + \
    '''/Hanyi Senty Candy-color.ttf");}'''
    
PDF_CSS_STYLE_GENERAL = PDF_CSS_BASE + \
    '''body{font-family:Cambria,Liberation Serif,Bitstream Vera Serif,Georgia,Times,Times New Roman,serif}h2{text-align:left;text-transform:uppercase;font-weight:200}ol{list-style-type:none}ol>li:first-child{margin-top:.3em}nav[epub|type~=toc]>ol>li>ol{list-style-type:square}nav[epub|type~=toc]>ol>li>ol>li{margin-top:.3em}p{font-size: 1.8rem;}h1{text-transform: uppercase;font-size: 3rem;}a{padding: 3px 3px;font-weight: bold;text-transform: uppercase;color: #272727;border-radius: 7px;font-size: 2rem;}h2{margin: 0px 0px 0px 0px;font-size: 2.5rem; text-transform: uppercase !important;text-align:center}'''


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
        #rmfile(_out_fname)
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


def set_encode_style(encode_style=0):
    if encode_style == 0:
        return PDF_CSS_STYLE_GENERAL
    elif encode_style == 1:
        return PDF_CSS_STYLE_RUSSIAN
    elif encode_style == 2:
        return PDF_CSS_STYLE_CHINESE
    return PDF_CSS_STYLE_GENERAL


def build_from_images_html(title, cover, sections, binary_response=False, resources=[], encode_style=0):
    """Build a epub file from html content with a section list

    :param title: Title of the book
    :param cover: Cover in HTML
    :param sections: Sections of the book, it has a list of chapters
    :param binary_response: Flag that assign if the response will has a binary file
    """
    """Create a book instance"""
    _source_html_cover = "<html>"
    _source_html_cover += "<head>"
    _source_html_cover += "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />"
    _source_html_cover += "<meta charset=\"UTF-8\">"
    _source_html_cover += "<style>{0}</style>".format(
        set_encode_style(PDF_CSS_STYLE_GENERAL)
    )
    _source_html_cover += "</head>"
    _source_html_cover += "<body style=\"text-align: center; font-family: none;\">"
    _source_html_cover += cover
    _source_html_cover += "</body>"
    _source_html_cover += "</html>"

    """Generate folder"""
    _process_id = uuid.uuid1().hex
    _files_merge = []

    """Define out filename"""
    _out_fname = "{0}/{1}.pdf".format(
        PDF_OUT_PATH,
        _process_id
    )
    _out_fname_cover = "{0}/{1}-cover.pdf".format(
        PDF_OUT_PATH,
        _process_id
    )
    # open output file for writing (truncated binary)
    _result_file_cover = open(_out_fname_cover, "w+b")

    """Write pdfs file"""
    # convert HTML to PDF
    _file_cover = pisa.CreatePDF(
        _source_html_cover,
        dest=_result_file_cover,
        encoding='UTF-8'
    )
    # close output file
    _result_file_cover.close()                 # close output file
    _files_merge.append(
        _out_fname_cover
    )

    if sections:

        _out_fname_content = "{0}/{1}-content.pdf".format(
            PDF_OUT_PATH,
            _process_id
        )

        _source_html_content = "<html>"
        _source_html_content += "<head>"
        _source_html_content += "<style>{0}</style>".format(
            set_encode_style(encode_style)
        )
        _source_html_content += "</head>"
        _source_html_content += "<body style=\"text-align: center; font-family: Roboto, sans-serif !important; padding-right: 100px !important; padding-left: 100px !important; margin-right: 100px !important; margin-left: 100px !important;\">"

        """For each section do the following"""
        for _idx_sec, _section in enumerate(sections):
            """For each chapter do the following"""
            for _idx_ch, _chapter in enumerate(_section['chapters']):
                """Set valid chapter format"""
                _source_html_content += _chapter['content']

        _result_file_content = open(_out_fname_content, "w+b")

        _source_html_content += "</body>"
        _source_html_content += "</html>"

        _file_content = pisa.CreatePDF(
            _source_html_content,
            dest=_result_file_content
        )
        _result_file_content.close()                 # close output file
        _files_merge.append(
            _out_fname_content
        )

    def add_resource(_resource):
        try:
            """Add resources"""
            if _resource['type'] == 'image_url':
                _image_item = get_resource_image_item(
                    _resource['url'],
                    _resource['file_name'],
                    _resource.get('headers')
                )
                if not _image_item:
                    return None
                # add Image file
                _out_fname_content_ch = "{0}/chapter-{1}.pdf".format(
                    PDF_OUT_PATH,
                    uuid.uuid1().hex
                )
                with open(_out_fname_content_ch, "w+b") as out_file:
                    out_file.write(img2pdf.convert(_image_item['binary']))

                _files_merge.append(
                    _out_fname_content_ch
                )
        except Exception as err:
            print(err)
            pass

    for _resource in resources:
        add_resource(_resource)

    """Merge all pdfs"""
    merger_pdf(
        _out_fname,
        _files_merge
    )
    """Get size of file"""
    _size = os.path.getsize(_out_fname)
    """Check if binary response is True"""
    if binary_response == "True":
        """Get content from the file"""
        _data_b64 = binascii.b2a_base64(
            get_content_from_file(_out_fname)
        ).decode('utf-8')
    else:
        _data_b64 = None
    """Delete file"""
    rmfile(_out_fname)
    rmfile(_out_fname_cover)
    rmfile(_out_fname_content)
    """Transform name"""
    if not title:
        title = _process_id

    """Transform data response"""
    _pdf = {
        u"title": title,
        u"pdf_title": slugify(title)+".pdf",
        u"pdf_size": _size,
        u"pdf_id": _process_id,
        u"pdf_b64": _data_b64
    }
    """Return epub url reference"""
    return success_response_service(
        data=_pdf
    )


def get_content_from_file(fname):
    """Get all content from a file

    :param fname: Name of the file to get information.
    """

    """Open the file"""
    _book = open(fname, "rb")
    """Read the book"""
    _content = _book.read()
    """Close the file"""
    _book.close()
    """Return data"""
    return _content


def merger_pdf(output_path, input_paths):
    pdf_writer = PdfFileWriter()
    for path in input_paths:
        pdf_reader = PdfFileReader(path)
        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))
    with open(output_path, 'wb') as fh:
        pdf_writer.write(fh)


def get_resource_image_item(url, file_name, headers={}):
    # load Image file
    _binary_image = get_download_item_req(url, headers)
    """Check that this one havenot errors"""
    if not _binary_image:
        return None
    return _binary_image


def get_download_item_req(url, headers):
    """Download items asynchronously"""
    with requests.get(url=url, headers=headers) as response:
        _downloaded_item = response.content
        if _downloaded_item:
            return {
                u'binary': _downloaded_item,
                u'filename': url.split('/')[-1]
            }
        else:
            return None
