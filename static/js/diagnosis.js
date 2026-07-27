/**
 * diagnosis.js
 * ------------
 * スマホ向けカード型診断 UI。
 * タップで選択 → 自動で次の質問へ（最終問は結果送信）。
 * 2問目以降は「前の質問へ」で戻れる。
 */

document.addEventListener("DOMContentLoaded", function () {
    const panels = document.querySelectorAll(".question-panel");
    const form = document.getElementById("diagnosis-form");
    const progressFill = document.getElementById("progress-fill");
    const currentNum = document.getElementById("current-num");
    const nav = document.getElementById("diagnosis-nav");
    const btnBack = document.getElementById("btn-back");
    const btnNext = document.getElementById("btn-next");
    const total = panels.length;
    let currentIndex = 0;
    let isTransitioning = false;

    function syncHiddenInput(choiceId, qIndex) {
        let hidden = form.querySelector(`input[name="choice_id"][data-q="${qIndex}"]`);
        if (!hidden) {
            hidden = document.createElement("input");
            hidden.type = "hidden";
            hidden.name = "choice_id";
            hidden.dataset.q = qIndex;
            form.appendChild(hidden);
        }
        hidden.value = choiceId;
    }

    function getSelectedChoiceId(qIndex) {
        const hidden = form.querySelector(`input[name="choice_id"][data-q="${qIndex}"]`);
        return hidden ? hidden.value : null;
    }

    function restoreSelection(panel, qIndex) {
        const choiceId = getSelectedChoiceId(qIndex);
        panel.querySelectorAll(".choice-card-btn").forEach((card) => {
            card.classList.toggle("selected", choiceId !== null && card.dataset.choiceId === choiceId);
        });
    }

    function updateProgress(index) {
        currentNum.textContent = index + 1;
        progressFill.style.width = ((index + 1) / total * 100) + "%";
    }

    function updateNav(index) {
        const isFirst = index === 0;
        btnBack.hidden = isFirst;
        nav.classList.toggle("diagnosis-nav-first", isFirst);
        btnNext.disabled = !getSelectedChoiceId(index);
    }

    function showPanel(index) {
        currentIndex = index;
        panels.forEach((panel, i) => panel.classList.toggle("active", i === index));
        restoreSelection(panels[index], index);
        updateProgress(index);
        updateNav(index);
    }

    function goNext() {
        if (!getSelectedChoiceId(currentIndex) || isTransitioning) return;

        if (currentIndex < total - 1) {
            showPanel(currentIndex + 1);
            return;
        }

        form.submit();
    }

    function goBack() {
        if (currentIndex === 0 || isTransitioning) return;
        showPanel(currentIndex - 1);
    }

    function selectCard(card, panel, index) {
        if (isTransitioning) return;

        const choiceId = card.dataset.choiceId;
        const qIndex = card.dataset.question;

        panel.querySelectorAll(".choice-card-btn").forEach((c) => c.classList.remove("selected"));
        card.classList.add("selected");
        syncHiddenInput(choiceId, qIndex);
        updateNav(index);

        isTransitioning = true;

        setTimeout(() => {
            if (index < total - 1) {
                showPanel(index + 1);
                isTransitioning = false;
            } else {
                form.submit();
            }
        }, 450);
    }

    panels.forEach((panel, index) => {
        panel.querySelectorAll(".choice-card-btn").forEach((card) => {
            card.addEventListener("click", () => selectCard(card, panel, index));
        });
    });

    btnBack.addEventListener("click", goBack);
    btnNext.addEventListener("click", goNext);

    showPanel(0);
});
