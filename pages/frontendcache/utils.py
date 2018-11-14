import logging

from wagtail.contrib.wagtailfrontendcache.utils import get_backends

logger = logging.getLogger(__name__)


def purge_all_from_cache(backend_settings=None, backends=None):
    """Utility method to purge all from cache, based on 
    wagtail.contrib.wagtailfrontendcache.utils"""
    
    for backend_name, backend in get_backends(backend_settings=backend_settings, backends=backends).items():
        """Check that backend has purge_all implemented"""
        try:
            logger.info("[%s] Purging All", backend_name)            
            backend.purge_all()
        except AttributeError:
            logger.error("[%s] Backend does not support purge_all.", backend_name)
