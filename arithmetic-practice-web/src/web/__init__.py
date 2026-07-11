"""
Flask Web应用工厂。

使用应用工厂模式（Application Factory Pattern）创建Flask实例，
支持蓝图注册、配置管理、错误处理。

蓝图组织：
  - main_bp: 主页面路由
  - api_bp:  JSON API 路由（供AJAX调用）
"""

import os
from flask import Flask, render_template


def create_app(db_path: str = None, config: dict = None) -> Flask:
    """创建并配置Flask应用。

    Args:
        db_path: SQLite数据库路径。
        config: 额外配置字典。

    Returns:
        配置好的 Flask 应用实例。
    """
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static',
    )

    # -- 基础配置 --
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY', 'math-practice-dev-key-2024',
    )
    app.config['DB_PATH'] = db_path or os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'data', 'mathpractice.db',
    )

    if config:
        app.config.update(config)

    # -- 注册蓝图 --
    from web.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # -- 错误处理 --
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    return app


def get_application():
    """获取 Application 实例（延迟创建，复用数据库连接）。

    在请求上下文中获取或创建 Application 单例。
    """
    from flask import g, current_app
    if 'app' not in g:
        from app import Application
        g.app = Application(db_path=current_app.config['DB_PATH'])
    return g.app
