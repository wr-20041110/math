"""数据库仓库 CRUD + 分析查询测试。"""
import pytest
import os
import tempfile
from src.db.connection import ConnectionManager
from src.db.repository import DatabaseRepository
from src.db.schema import create_schema


@pytest.fixture
def repo():
    """在临时数据库中创建测试仓库。"""
    db_path = os.path.join(tempfile.gettempdir(), "test_mathpractice.db")
    ConnectionManager.reset()
    r = DatabaseRepository(db_path)
    yield r
    r.reset()
    r.close()


@pytest.fixture
def students(repo):
    """预注册 3 个测试学生。"""
    return [
        repo.register_student("Alice", "Grade3"),
        repo.register_student("Bob", "Grade3"),
        repo.register_student("Charlie", "Grade4"),
    ]


class TestStudentCRUD:
    def test_register_new_student(self, repo):
        sid = repo.register_student("TestStudent", "Grade1")
        assert sid > 0

    def test_register_duplicate_returns_existing(self, repo):
        sid1 = repo.register_student("DupStudent")
        sid2 = repo.register_student("DupStudent")
        assert sid1 == sid2

    def test_list_students(self, repo, students):
        rows = repo.list_students()
        assert len(rows) == 3

    def test_find_existing_student(self, repo, students):
        row = repo.find_student("Alice")
        assert row is not None
        assert row["name"] == "Alice"

    def test_find_nonexistent_student(self, repo):
        assert repo.find_student("Nobody") is None


class TestExerciseCRUD:
    def test_save_and_load_exercise(self, repo):
        from core.operators import Addition, Subtraction
        from core.problem import Problem
        from models.exercise import Exercise

        problems = [
            Problem(15, 7, Addition()),
            Problem(88, 21, Subtraction()),
            Problem(44, 23, Addition()),
        ]
        ex = Exercise(exercise_id="EX-TEST-001", exercise_type="mixed", problems=problems)
        repo.save_exercise(ex)

        loaded = repo.load_exercise("EX-TEST-001")
        assert loaded.exercise_id == "EX-TEST-001"
        assert loaded.problem_count == 3
        assert loaded.problems[0].left == 15
        assert loaded.problems[1].answer == 67

    def test_load_nonexistent_exercise_raises(self, repo):
        with pytest.raises(ValueError, match="不存在"):
            repo.load_exercise("EX-NOT-EXIST")


class TestAnswerSubmission:
    def test_submit_all_correct_answers(self, repo, students):
        from core.operators import Addition
        from core.problem import Problem
        from models.exercise import Exercise

        ex = Exercise(exercise_id="EX-A-001", exercise_type="addition",
                     problems=[Problem(5, 3, Addition()), Problem(10, 20, Addition())])
        repo.save_exercise(ex)

        result = repo.submit_answers("EX-A-001", students[0],
                                     {1: 8, 2: 30})
        assert result["total"] == 2
        assert result["correct"] == 2
        assert result["wrong"] == 0
        assert result["percentage"] == 100.0

    def test_submit_with_errors(self, repo, students):
        from core.operators import Subtraction
        from core.problem import Problem
        from models.exercise import Exercise

        ex = Exercise(exercise_id="EX-A-002", exercise_type="subtraction",
                     problems=[Problem(80, 20, Subtraction()), Problem(55, 10, Subtraction())])
        repo.save_exercise(ex)

        result = repo.submit_answers("EX-A-002", students[1],
                                     {1: 60, 2: 44})  # 第二题错(45), 第一题对(60)
        assert result["total"] == 2
        assert result["correct"] == 1  # 80-20=60 correct
        assert result["wrong"] == 1    # 55-10=45, student said 44
        assert 2 in result["wrong_indices"]


class TestAnalysisQueries:
    def test_class_overview(self, repo, students):
        # 先造数据
        from core.operators import Addition
        from core.problem import Problem
        from models.exercise import Exercise

        ex = Exercise(exercise_id="EX-O-001", exercise_type="addition",
                     problems=[Problem(5, 3, Addition())])
        repo.save_exercise(ex)
        repo.submit_answers("EX-O-001", students[0], {1: 8})
        repo.submit_answers("EX-O-001", students[1], {1: 7})  # wrong

        overview = repo.class_overview()
        assert len(overview) == 3  # all 3 students

    def test_weak_problems_analysis(self, repo, students):
        from core.operators import Addition
        from core.problem import Problem
        from models.exercise import Exercise

        ex = Exercise(exercise_id="EX-W-001", exercise_type="addition",
                     problems=[Problem(15, 7, Addition())])
        repo.save_exercise(ex)
        # 所有学生都做错这道题
        for sid in students:
            repo.submit_answers("EX-W-001", sid, {1: 999})

        weak = repo.weak_problems_analysis()
        assert len(weak) >= 1
        assert weak[0]["wrong_count"] == 3
        assert weak[0]["error_rate"] == 100.0

    def test_student_progress(self, repo, students):
        from core.operators import Addition
        from core.problem import Problem
        from models.exercise import Exercise

        ex = Exercise(exercise_id="EX-P-001", exercise_type="addition",
                     problems=[Problem(5, 3, Addition())])
        repo.save_exercise(ex)
        repo.submit_answers("EX-P-001", students[0], {1: 8})

        progress = repo.student_progress(students[0])
        assert len(progress) == 1

    def test_database_stats(self, repo, students):
        from core.operators import Addition
        from core.problem import Problem
        from models.exercise import Exercise

        ex = Exercise(exercise_id="EX-S-001", exercise_type="addition",
                     problems=[Problem(1, 1, Addition())])
        repo.save_exercise(ex)
        repo.submit_answers("EX-S-001", students[0], {1: 2})

        stats = repo.database_stats()
        assert stats["student_count"] == 3
        assert stats["exercise_count"] == 1
        assert stats["problem_count"] == 1
        assert stats["answer_count"] == 1
        assert stats["score_count"] == 1
