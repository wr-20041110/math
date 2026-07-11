/**
 * 口算练习系统 —— 在线练习交互脚本
 *
 * 功能：
 *   - 计时器
 *   - AJAX 答案提交
 *   - 实时反馈（正确/错误高亮）
 *   - 键盘导航（回车跳转下一题）
 */

// ---- 计时器 ----
let timerInterval = null;
let startTime = null;

function startTimer() {
    startTime = Date.now();
    timerInterval = setInterval(updateTimer, 1000);
}

function updateTimer() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const min = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const sec = String(elapsed % 60).padStart(2, '0');
    const display = document.getElementById('time-display');
    if (display) {
        display.textContent = min + ':' + sec;
    }
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

// ---- 答案提交 ----
async function submitAnswers() {
    const exerciseId = document.getElementById('exercise-id').value;
    const student = document.getElementById('student-name').value;
    const count = parseInt(document.getElementById('problem-count').value);
    const submitBtn = document.getElementById('submit-btn');

    // 收集答案
    const answers = {};
    let hasAnswer = false;
    for (let i = 1; i <= count; i++) {
        const input = document.getElementById('answer-' + i);
        if (input && input.value.trim() !== '') {
            const val = parseInt(input.value, 10);
            if (!isNaN(val)) {
                answers[i] = val;
                hasAnswer = true;
            }
        }
    }

    if (!hasAnswer) {
        alert('请至少填写一道题的答案！');
        return;
    }

    // 禁用按钮
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 批改中...';

    stopTimer();

    try {
        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                exercise_id: exerciseId,
                student: student,
                answers: answers
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || '提交失败');
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        alert('提交失败: ' + error.message);
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-check-circle"></i> 提交答案';
    }
}

// ---- 结果显示 ----
function displayResults(result) {
    const count = parseInt(document.getElementById('problem-count').value);

    // 逐题标记
    for (let i = 1; i <= count; i++) {
        const item = document.getElementById('problem-' + i);
        const feedback = document.getElementById('feedback-' + i);
        const input = document.getElementById('answer-' + i);

        if (!item) continue;

        if (result.wrong_indices && result.wrong_indices.includes(i)) {
            item.classList.add('wrong');
            if (feedback) feedback.className = 'feedback-icon wrong';
        } else if (input && input.value.trim() !== '') {
            item.classList.add('correct');
            if (feedback) feedback.className = 'feedback-icon correct';
        }

        // 禁用输入
        if (input) input.disabled = true;
    }

    // 显示结果区域
    const resultArea = document.getElementById('result-area');
    if (resultArea) {
        resultArea.style.display = 'block';
    }

    // 更新分数
    const scoreDisplay = document.getElementById('score-display');
    if (scoreDisplay) {
        scoreDisplay.textContent = result.percentage + '%';
        scoreDisplay.className = 'display-4 mb-0 ' + (
            result.percentage >= 80 ? 'text-success' :
            result.percentage >= 60 ? 'text-warning' : 'text-danger'
        );
    }

    const correctDisplay = document.getElementById('correct-display');
    if (correctDisplay) correctDisplay.textContent = result.correct;

    const wrongDisplay = document.getElementById('wrong-display');
    if (wrongDisplay) wrongDisplay.textContent = result.wrong;

    // 禁用提交按钮
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = '已提交';
        submitBtn.className = 'btn btn-secondary btn-lg px-5';
    }

    // 滚动到结果区
    resultArea?.scrollIntoView({ behavior: 'smooth' });
}

// ---- 清空答案 ----
function resetAnswers() {
    const count = parseInt(document.getElementById('problem-count').value);
    for (let i = 1; i <= count; i++) {
        const input = document.getElementById('answer-' + i);
        if (input) {
            input.value = '';
            input.disabled = false;
            input.className = 'answer-input form-control';
        }
        const item = document.getElementById('problem-' + i);
        if (item) {
            item.classList.remove('correct', 'wrong');
        }
        const feedback = document.getElementById('feedback-' + i);
        if (feedback) {
            feedback.className = 'feedback-icon';
        }
    }

    // 隐藏结果
    const resultArea = document.getElementById('result-area');
    if (resultArea) {
        resultArea.style.display = 'none';
    }

    // 恢复按钮
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-check-circle"></i> 提交答案';
        submitBtn.className = 'btn btn-success btn-lg px-5';
    }

    // 重启计时器
    startTimer();
}

// ---- 键盘导航 ----
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter 提交
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        submitAnswers();
        return;
    }

    // Enter 跳转到下一题
    if (e.key === 'Enter' && e.target.classList.contains('answer-input')) {
        e.preventDefault();
        const currentIndex = parseInt(e.target.dataset.index);
        const nextInput = document.getElementById('answer-' + (currentIndex + 1));
        if (nextInput) {
            nextInput.focus();
            nextInput.select();
        } else {
            // 最后一题，提交
            submitAnswers();
        }
    }
});

// ---- 页面加载完成 ----
document.addEventListener('DOMContentLoaded', function() {
    // 聚焦第一个输入框
    const firstInput = document.getElementById('answer-1');
    if (firstInput) firstInput.focus();

    // 启动计时器
    startTimer();

    // 输入框自动选中
    document.querySelectorAll('.answer-input').forEach(input => {
        input.addEventListener('focus', function() {
            this.select();
        });
    });
});
