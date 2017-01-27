from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from wagtail.wagtaildocs.models import Document

def serve_wagtail_doc(request, document_id, document_filename):
    """
    Replacement for ``wagtail.wagtaildocs.views.serve.serve``
    Wagtail's default document view serves everything as an attachment.
    We'll bounce back to the URL and let the media server serve it.
    """
    doc = get_object_or_404(Document, id=document_id)
    return HttpResponseRedirect(doc.file.url)
