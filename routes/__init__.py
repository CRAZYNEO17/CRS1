def register_routes(app):
    from .schemes import schemes_bp
    from .state_crops import state_crops_bp
    app.register_blueprint(schemes_bp)
    app.register_blueprint(state_crops_bp)