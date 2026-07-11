"""DatabaseRepository CRUD + 分析查询测试。"""
import pytest
from core.operators import Addition, Subtraction
from core.problem import Problem
from models.exercise import Exercise


class TestStudentCRUD:
    def test_register_new_student(self, repo):
        sid = repo.register_student("TestStudent", "Grade1")
        assert sid > 0

    def test_register_duplicate_returns_existing(self, repo):
        sid1 = repo.register_student("DupStudent")
        sid2 = repo.register_student("DupStudent")
        assert sid1 == sid2

    def test_list_students(self, repo, sample_students):
        rows = repo.list_students()
        assert len(rows) == 3

    def test_find_existing_student(self, repo, sample_students):
        row = repo.find_student("Alice")
        assert row is not None
        assert row["name"] == "Alice"

    def test_find_nonexistent_student(self, repo):
        assert repo.find_student("Nobody") is None


class TestExerciseCRUD:
    def test_save_and_load_exercise(self, repo):
        problems = [
            Problem(15, 7, Addition()),
            Problem(88, 21, Subtraction()),
            Problem(44, 23, Addition()),
        ]
        ex = Exercise("EX-TEST-001", "mixed", problems)
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
    def test_submit_all_correct(self, repo, sample_students):
        ex = Exercise("EX-A-001", "addition",
                      problems=[Problem(5, 3, Addition()), Problem(10, 20, Addition())])
        repo.save_exercise(ex)

        result = repo.submit_answers("EX-A-001", sample_students[0], {1: 8, 2: 30})
        assert result["total"] == 2
        assert result["correct"] == 2
        assert result["percentage"] == 100.0

    def test_submit_with_errors(self, repo, sample_students):
        ex = Exercise("EX-A-002", "subtraction",
                      problems=[Problem(80, 20, Subtraction()), Problem(55, 10, Subtraction())])
        repo.save_exercise(ex)

        result = repo.submit_answers("EX-A-002", sample_students[1],
                                     {1: 60, 2: 44})  # 第二题错
        assert result["correct"] == 1
        assert result["wrong"] == 1
        assert 2 in result["wrong_indices"]


class TestAnalysisQueries:
    def test_class_overview(self, repo, sample_students):
        ex = Exercise("EX-O-001", "addition",
                      problems=[Problem(5, 3, Addition())])
        repo.save_exercise(ex)
        repo.submit_answers("EX-O-001", sample_students[0], {1: 8})
        repo.submit_answers("EX-O-001", sample_students[1], {1: 7})

        overview = repo.class_overview()
        assert len(overview) == 3

    def test_weak_problems_analysis(self, repo, sample_students):
        ex = Exercise("EX-W-001", "addition",
                      problems=[Problem(15, 7, Addition())])
        repo.save_exercise(ex)
        for sid in sample_students:
            repo.submit_answers("EX-W-001", sid, {1: 999})

        weak = repo.weak_problems_analysis()
        assert len(weak) >= 1
        assert weak[0]["wrong_count"] == 3

    def test_student_progress(self, repo, sample_students):
        ex = Exercise("EX-P-001", "addition",
                      problems=[Problem(5, 3, Addition())])
        repo.save_exercise(ex)
        repo.submit_answers("EX-P-001", sample_students[0], {1: 8})

        progress = repo.student_progress(sample_students[0])
        assert len(progress) == 1

    def test_database_stats(self, repo, sample_students):
        ex = Exercise("EX-S-001", "addition",
                      problems=[Problem(1, 1, Addition())])
        repo.save_exercise(ex)
        repo.submit_answers("EX-S-001", sample_students[0], {1: 2})

        stats = repo.database_stats()
        assert stats["student_count"] == 3
        assert stats["exercise_count"] == 1
        assert stats["problem_count"] == 1
        assert stats["answer_count"] == 1
        assert stats["score_count"] == 1
