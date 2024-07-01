from fastapi import APIRouter, Response

from app.services.qrcode_gen import qrcode_generator

router = APIRouter(prefix="/generate_qr", tags=["qrcode"])


@router.get("/")
async def generate_qr(url: str):
    """
    Generate QR-code

    :param url: String to QR-code.
    :type url: str
    :return: Picture.
    :rtype: media_type="image/svg+xml"
    """    
    qr = await qrcode_generator(url)
    return Response(content=qr, media_type="image/svg+xml")
