import io
import qrcode
from qrcode.image.svg import SvgImage


async def qrcode_generator(url):
    """
    Qrcode generator

    Args:
        url (str):  Cloudinary URL
    Returns:
        file.xml:  QR-code picture
    """    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white", image_factory=SvgImage)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr)
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr
