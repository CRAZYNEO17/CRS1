def register_routes(app):
    from .schemes import schemes_bp
    from .state_crops import state_crops_bp
    from .recommendation import recommendation_bp
    from .health import health_bp
    from .crops import crops_bp
    from .weather import weather_bp
    from .yield_routes import yield_routes_bp
    app.register_blueprint(schemes_bp)
    app.register_blueprint(state_crops_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(crops_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(yield_routes_bp)