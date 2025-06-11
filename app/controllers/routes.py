from flask import Blueprint, request # type: ignore

general_bp = Blueprint('general', __name__)

@general_bp.route('/logs', methods=['POST'])
def logs():
    """
    DEFINITION DE LA REQUETE
    """
    return {"status": "success", "message": "Log received"}, 200

@general_bp.route('/format', methods=['POST'])
def formatMessage():
    """
    DEFINITION DE LA REQUETE
    """
    body = request.get_json()
    return {"status": "success", "message": "Format received"}, 200