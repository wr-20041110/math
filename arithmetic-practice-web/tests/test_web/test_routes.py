"""Web路由单元测试（使用Flask测试客户端）。"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))


@pytest.fixture
def app():
    """创建测试用Flask应用。"""
    import tempfile
    from web import create_app

    fd, db_path = tempfile.mkstemp(suffix='.db', prefix='test_web_')
    os.close(fd)

    app = create_app(db_path=db_path)
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost'

    yield app

    # 关闭可能的数据库连接
    try:
        from db.connection import ConnectionManager
        ConnectionManager.reset()
    except Exception:
        pass

    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except PermissionError:
        pass  # Windows文件锁定，跳过清理


@pytest.fixture
def client(app):
    """Flask测试客户端。"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI测试运行器。"""
    return app.test_cli_runner()


class TestHomePage:
    """首页测试。"""

    def test_index_returns_200(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_index_contains_keywords(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '口算练习' in html

    def test_analysis_page(self, client):
        response = client.get('/analysis')
        assert response.status_code == 200


class TestExerciseGeneration:
    """习题生成测试。"""

    def test_generate_exercise_requires_student(self, client):
        """没有学生姓名应重定向。"""
        response = client.post('/exercise/generate', data={
            'type': 'mixed',
            'count': '10',
            'student': '',
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_generate_exercise_success(self, client):
        """成功生成习题并重定向到练习页。"""
        response = client.post('/exercise/generate', data={
            'type': 'mixed',
            'count': '10',
            'student': 'TestStudent',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '口算练习' in response.data.decode('utf-8')


class TestAPI:
    """API路由测试。"""

    def test_submit_no_data(self, client):
        response = client.post('/api/submit', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_submit_missing_fields(self, client):
        response = client.post('/api/submit', json={
            'exercise_id': 'EX-001',
            # 缺少 student
            'answers': {'1': 42},
        })
        assert response.status_code == 400

    def test_submit_invalid_answers(self, client):
        response = client.post('/api/submit', json={
            'exercise_id': 'EX-001',
            'student': 'Test',
            'answers': {},
        })
        assert response.status_code == 400

    def test_students_api(self, client):
        response = client.get('/api/students')
        assert response.status_code == 200
        assert isinstance(response.get_json(), list)


class TestExport:
    """导出路由测试。"""

    def test_export_nonexistent_exercise(self, client):
        response = client.get('/export/word/EX-NOT-EXIST', follow_redirects=True)
        assert response.status_code == 200


class TestErrorPages:
    """错误页面测试。"""

    def test_404_page(self, client):
        response = client.get('/nonexistent-page')
        assert response.status_code == 404


class TestHistory:
    """历史页面测试。"""

    def test_history_nonexistent_student(self, client):
        response = client.get('/history/NonExistentStudent', follow_redirects=True)
        assert response.status_code == 200
