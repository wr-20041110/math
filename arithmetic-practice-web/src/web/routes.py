"""
Flask路由定义。

路由设计：
  主页面 (main_bp):
    GET  /                         —— 首页
    GET  /exercise/<exercise_id>   —— 习题练习页
    POST /exercise/generate        —— 生成新习题
    GET  /result/<exercise_id>/<student> —— 批改结果页
    GET  /analysis                 —— 成绩分析页
    GET  /history/<student>        —— 学生练习历史

  API (api_bp):
    POST /api/submit               —— 提交答案（JSON）
    GET  /api/chart/<type>         —— 获取图表（Base64）
    GET  /api/export/word/<id>     —— 下载Word文档
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify, session, send_file, g,
)
import os
import tempfile
from datetime import datetime

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)


# ======================================================================
# 辅助函数
# ======================================================================

def _get_app():
    """获取 Application 实例。"""
    from flask import current_app
    if 'app' not in g:
        from app import Application
        g.app = Application(db_path=current_app.config['DB_PATH'])
    return g.app


def _get_ex_types():
    """获取可用的习题类型。"""
    return [
        ('mixed', '混合加减'),
        ('addition', '纯加法'),
        ('subtraction', '纯减法'),
    ]


# ======================================================================
# 主页面路由
# ======================================================================

@main_bp.route('/')
def index():
    """首页 —— 欢迎页面 + 快速操作入口。"""
    app = _get_app()
    students = app.list_students()
    exercises = app.repo.list_recent_exercises(10)
    stats = app.stats()
    return render_template(
        'index.html',
        students=students,
        exercises=exercises,
        stats=stats,
        exercise_types=_get_ex_types(),
    )


@main_bp.route('/exercise/generate', methods=['POST'])
def generate_exercise():
    """生成新习题并跳转到练习页。"""
    ex_type = request.form.get('type', 'mixed')
    count = int(request.form.get('count', 20))
    student = request.form.get('student', '').strip()

    if not student:
        flash('请输入学生姓名', 'warning')
        return redirect(url_for('main.index'))

    if count < 5 or count > 100:
        flash('题目数量需在 5-100 之间', 'warning')
        return redirect(url_for('main.index'))

    app = _get_app()
    exercise = app.generate_and_save(ex_type, count)

    # 存储当前练习信息到会话
    session['current_exercise'] = exercise.exercise_id
    session['current_student'] = student

    return redirect(url_for('main.practice', exercise_id=exercise.exercise_id))


@main_bp.route('/exercise/<exercise_id>')
def practice(exercise_id):
    """习题练习页面。"""
    app = _get_app()
    try:
        exercise = app.load_exercise(exercise_id)
    except ValueError:
        flash('习题不存在', 'danger')
        return redirect(url_for('main.index'))

    student = session.get('current_student', '')
    return render_template(
        'exercise.html',
        exercise=exercise,
        student=student,
    )


@main_bp.route('/result/<exercise_id>/<student>')
def result(exercise_id, student):
    """批改结果页面。"""
    app = _get_app()
    try:
        exercise = app.load_exercise(exercise_id)
    except ValueError:
        flash('习题不存在', 'danger')
        return redirect(url_for('main.index'))

    # 获取最近一次成绩
    student_rec = app.find_student(student)
    if not student_rec:
        flash('学生不存在', 'danger')
        return redirect(url_for('main.index'))

    scores = app.repo.student_scores(student_rec['id'])
    latest_score = scores[0] if scores else None

    return render_template(
        'result.html',
        exercise=exercise,
        student=student,
        score=latest_score,
    )


@main_bp.route('/analysis')
def analysis():
    """成绩分析页面。"""
    app = _get_app()

    student_name = request.args.get('student', '').strip()

    overview = app.class_overview()
    weak_all = app.weak_problems(20)

    student_data = None
    student_weak = None
    if student_name:
        try:
            student_data = app.student_progress(student_name)
            student_weak = app.student_weak(student_name, 10)
        except ValueError:
            flash(f'学生 "{student_name}" 不存在', 'warning')

    return render_template(
        'analysis.html',
        overview=overview,
        weak_all=weak_all,
        student_name=student_name,
        student_data=student_data,
        student_weak=student_weak,
    )


@main_bp.route('/history/<student>')
def history(student):
    """学生练习历史页面。"""
    app = _get_app()
    try:
        progress = app.student_progress(student)
    except ValueError:
        flash(f'学生 "{student}" 不存在', 'danger')
        return redirect(url_for('main.index'))

    return render_template(
        'history.html',
        student=student,
        progress=progress,
    )


@main_bp.route('/export/word/<exercise_id>')
def export_word(exercise_id):
    """下载习题Word文档。"""
    from export.word_exporter import WordExporter

    app = _get_app()
    try:
        exercise = app.load_exercise(exercise_id)
    except ValueError:
        flash('习题不存在', 'danger')
        return redirect(url_for('main.index'))

    exporter = WordExporter()
    tmp_path = os.path.join(tempfile.gettempdir(), f"{exercise_id}.docx")
    exporter.export_exercise(exercise, tmp_path, include_answers=True)

    return send_file(
        tmp_path,
        as_attachment=True,
        download_name=f"{exercise_id}.docx",
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )


# ======================================================================
# API 路由（AJAX）
# ======================================================================

@api_bp.route('/submit', methods=['POST'])
def submit_answers():
    """提交答案并返回判题结果（JSON）。

    请求体:
        {
            "exercise_id": "EX-...",
            "student": "小明",
            "answers": {"1": 42, "2": 67, ...}
        }

    响应:
        {
            "total": 20,
            "correct": 18,
            "wrong": 2,
            "percentage": 90.0,
            "wrong_indices": [3, 7]
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求体为空'}), 400

    exercise_id = data.get('exercise_id')
    student = data.get('student', '').strip()
    raw_answers = data.get('answers', {})

    if not exercise_id or not student:
        return jsonify({'error': '缺少 exercise_id 或 student'}), 400

    # 转换答案为 int key → int value
    answers = {}
    for k, v in raw_answers.items():
        try:
            answers[int(k)] = int(v)
        except (ValueError, TypeError):
            continue

    if not answers:
        return jsonify({'error': '没有有效的答案'}), 400

    app = _get_app()
    try:
        result = app.submit_and_grade(exercise_id, student, answers)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(result)


@api_bp.route('/chart/<chart_type>')
def get_chart(chart_type):
    """获取图表（返回Base64编码的PNG）。"""
    from chart.chart_renderer import ChartRenderer

    app = _get_app()
    student = request.args.get('student', '').strip()
    renderer = ChartRenderer()

    if chart_type == 'trend':
        if not student:
            return jsonify({'error': '缺少 student 参数'}), 400
        try:
            progress = app.student_progress(student)
        except ValueError:
            return jsonify({'error': f'学生 "{student}" 不存在'}), 404
        if not progress:
            return jsonify({'error': '没有练习记录'}), 404
        b64 = renderer.plot_score_trend(progress, student, as_base64=True)

    elif chart_type == 'weak':
        weak = app.weak_problems(15)
        if not weak:
            return jsonify({'error': '没有弱项数据'}), 404
        b64 = renderer.plot_weak_bar(weak, as_base64=True)

    elif chart_type == 'comparison':
        overview = app.class_overview()
        if not overview:
            return jsonify({'error': '没有数据'}), 404
        b64 = renderer.plot_student_comparison(overview, as_base64=True)

    elif chart_type == 'multi':
        if not student:
            return jsonify({'error': '缺少 student 参数'}), 400
        try:
            progress = app.student_progress(student)
        except ValueError:
            return jsonify({'error': f'学生 "{student}" 不存在'}), 404
        if not progress:
            return jsonify({'error': '没有练习记录'}), 404
        b64 = renderer.plot_multi_session_bars(progress, student, as_base64=True)

    else:
        return jsonify({'error': f'未知图表类型: {chart_type}'}), 400

    if b64:
        return jsonify({'chart': f'data:image/png;base64,{b64}'})
    return jsonify({'error': '图表生成失败'}), 500


@api_bp.route('/students')
def list_students_api():
    """获取学生列表（JSON）。"""
    app = _get_app()
    students = app.list_students()
    return jsonify([
        {'id': s['id'], 'name': s['name'], 'grade': s['grade']}
        for s in students
    ])
