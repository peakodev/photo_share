import unittest
import io
import qrcode
from qrcode.image.svg import SvgImage
from app.services.qrcode_gen import qrcode_generator


class TestQRCodeGenerator(unittest.TestCase):
    async def test_qrcode_generator(self):
        test_url = "https://example.com"
        qr_code_bytes = await qrcode_generator(test_url)

        # Testing return type
        self.assertIsInstance(qr_code_bytes, bytes)

        # To verify the QR code contains the correct data, we can save it and read it back
        img_byte_arr = io.BytesIO(qr_code_bytes)
        img_byte_arr.seek(0)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(test_url)
        qr.make(fit=True)
        expected_img = qr.make_image(fill="black", back_color="white", image_factory=SvgImage)

        # Convert expected_img to bytes
        expected_img_byte_arr = io.BytesIO()
        expected_img.save(expected_img_byte_arr)
        expected_img_bytes = expected_img_byte_arr.getvalue()

        self.assertEqual(qr_code_bytes, expected_img_bytes)


if __name__ == "__main__":
    unittest.main()
