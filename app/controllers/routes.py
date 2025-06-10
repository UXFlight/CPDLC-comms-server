from flask import Blueprint

general_bp = Blueprint('general', __name__)

@general_bp.route('/logs', methods=['POST'])
def logs():
    """
    DEFINITION DE LA REQUETE
    """
    return {"status": "success", "message": "Log received"}, 200