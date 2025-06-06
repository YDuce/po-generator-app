from flask import request, jsonify
from flask import Blueprint
from werkzeug.utils import secure_filename
from pathlib import Path

from database import SessionLocal
from models import PORF, PORFLine, Product
from logic.porf_builder import draft_porf_xlsx
from api import api_bp as bp


@bp.route("/porf/upload", methods=["POST"])
def upload_porf():
    """Handle PORF+PO upload according to blueprint spec.

    This implementation is intentionally minimal: it stores metadata in the
    database and echoes a JSON response. Parsing of the XLSX rows and the
    associated PDF is *not* performed here; that logic belongs in dedicated
    helpers and will be fleshed out in future iterations.
    """

    if "file" not in request.files:
        return jsonify({"error": "file missing"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "filename missing"}), 400

    filename = secure_filename(file.filename)
    upload_path = Path("uploads") / filename
    upload_path.parent.mkdir(exist_ok=True)
    file.save(upload_path)

    # VERY naive PORF creation – real logic should parse XLSX
    db = SessionLocal()
    porf = PORF(porf_no=filename.split(".")[0], status="approved")
    db.add(porf)
    db.flush()

    # Fake line item linking to first product (or create dummy)
    product = db.query(Product).first()
    if product is None:
        product = Product(sku="DUMMY", title="Placeholder")
        db.add(product)
        db.flush()

    line = PORFLine(porf_id=porf.id, product_id=product.id, qty=1)
    db.add(line)
    db.commit()

    return jsonify({"message": "PORF uploaded", "porf_id": porf.id}), 201
