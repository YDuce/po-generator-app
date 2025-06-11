from flask import Blueprint, request, jsonify
from app.channels.woot.service import WootService

bp=Blueprint('woot',__name__,url_prefix='/api/woot')

@bp.route('/porf',methods=['POST'])
def create_porf():
    svc=WootService()
    p=svc.create_porf(request.get_json())
    return jsonify(p.to_dict()),201
