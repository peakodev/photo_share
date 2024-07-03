from fastapi import APIRouter, Response

from app.services.qrcode_gen import qrcode_generator

router = APIRouter(prefix="/generate_qr", tags=["qrcode"])


@router.get("/")
async def generate_qr(url: str):
    """
    Generate QR-code

    Args:
        url (str):  String to QR-code.
    Returns:
        media_type="image/svg+xml":  Picture.
    """    
    qr = await qrcode_generator(url)
    return Response(content=qr, media_type="image/svg+xml")
