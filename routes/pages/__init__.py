from .smart import smart_bp

def register_pages_blueprint(app):
    app.register_blueprint(smart_bp, url_prefix='/pages')
