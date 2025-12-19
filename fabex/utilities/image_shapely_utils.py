from .image_utils import image_to_chunks
from .shapely_utils import chunks_to_shapely


def image_to_shapely(o, i, with_border=False):
    """Convert an image to Shapely polygons.

    This function takes an image and converts it into a series of Shapely
    polygon objects. It first processes the image into chunks and then
    transforms those chunks into polygon geometries. The `with_border`
    parameter allows for the inclusion of borders in the resulting polygons.

    Args:
        o: The input image to be processed.
        i: Additional input parameters for processing the image.
        with_border (bool): A flag indicating whether to include
            borders in the resulting polygons. Defaults to False.

    Returns:
        list: A list of Shapely polygon objects created from the
            image chunks.
    """

    polychunks = image_to_chunks(o, i, with_border)
    polys = chunks_to_shapely(polychunks)

    return polys
