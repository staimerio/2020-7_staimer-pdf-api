# Retic
from retic import Router

# Controllers
import controllers.pdf as pdf

"""Define router instance"""
router = Router()

"""Define all paths - build"""
router.post("/build/from-epub", pdf.build_pdf_from_epub_list)