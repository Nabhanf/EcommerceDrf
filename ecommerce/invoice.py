from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from io import BytesIO

def generate_invoice(cart_items, total_amount, user_email):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.drawString(100, height - 100, "Invoice")
    p.drawString(100, height - 120, f"Email: {user_email}")
    p.drawString(100, height - 140, f"Total Amount: {total_amount / 100:.2f} INR")
    p.drawString(100, height - 160, "Items:")

    y = height - 180
    for item in cart_items:
        product_name = item['product']['name']
        product_price = item['product']['price']
        quantity = item['quantity']
        p.drawString(100, y, f"{product_name} - {quantity} pcs - {product_price * quantity / 100:.2f} INR")
        y -= 20

    p.showPage()
    p.save()

    buffer.seek(0)
    return ContentFile(buffer.read(), name='invoice.pdf')