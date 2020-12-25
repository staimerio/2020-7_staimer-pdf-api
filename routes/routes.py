# Retic
from retic import Router

# Controllers
import controllers.pdf as pdf

"""Define router instance"""
router = Router()

"""Define all paths - build"""
router.post("/build/from-epub", pdf.build_pdf_from_epub_list)
router.post("/build/from-epub2pdf", pdf.build_pdf_from_epub_list_ebook)


"""Define all paths - build"""
router.post("/build/from-images", pdf.build_from_images)
router.post("/build/from-html", pdf.build_from_html)
