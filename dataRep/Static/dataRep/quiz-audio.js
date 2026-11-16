(function() {
    const AudioContextConstructor =
        window.AudioContext || window.webkitAudioContext;
    const panel = document.createElement("div");
    const effectsButton = document.createElement("button");
    const musicButton = document.createElement("button");
    let audioContext = null;
    let effectsEnabled = true;
    let musicEnabled = false;
    let musicBus = null;
    let musicTimer = null;
    let chordIndex = 0;

    const style = document.createElement("style");
    style.textContent = `
        .quiz-audio-controls {
            position: fixed;
            right: 16px;
            bottom: 16px;
            z-index: 1000;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding: 8px;
            background: rgba(255, 253, 250, .96);
            border: 1px solid #e8dfcd;
            border-radius: 12px;
            box-shadow: 0 3px 14px rgba(37, 49, 41, .15);
        }
        .quiz-audio-controls button {
            min-height: 38px;
            padding: 8px 11px;
            border: 1px solid #d5cbb7;
            border-radius: 8px;
            background: #fff;
            color: #17382f;
            font: 600 12px/1.2 system-ui, sans-serif;
            cursor: pointer;
        }
        .quiz-audio-controls button:hover {
            background: #fff9ed;
            border-color: #e8b95b;
        }
        .quiz-audio-controls button:focus-visible {
            outline: 3px solid #e8b95b;
            outline-offset: 2px;
        }
        .quiz-audio-controls button:disabled {
            cursor: not-allowed;
            opacity: .7;
        }
        .quiz-feedback-message {
            margin: 16px 0;
            padding: 14px 16px;
            border-left: 5px solid;
            border-radius: 10px;
            font-weight: 800;
            animation: quiz-feedback-pop .3s ease-out;
        }
        .quiz-feedback-correct {
            border-color: #2f8750;
            background: #e9f5ec;
            color: #1c5632;
        }
        .quiz-feedback-incorrect {
            border-color: #a64e43;
            background: #fff0ed;
            color: #71342d;
        }
        .option.quiz-option-correct {
            border-color: #2f8750 !important;
            background: #e9f5ec !important;
            color: #1c5632 !important;
        }
        .option.quiz-option-incorrect {
            border-color: #a64e43 !important;
            background: #fff0ed !important;
            color: #71342d !important;
        }
        .quiz-score-bump {
            display: inline-block;
            animation: quiz-score-bump .45s ease-out;
        }
        .quiz-score-pop {
            display: inline-block;
            margin-left: 7px;
            color: #2f8750;
            font-size: .85em;
            font-weight: 800;
            animation: quiz-score-float .9s ease-out forwards;
        }
        @keyframes quiz-feedback-pop {
            from { opacity: 0; transform: translateY(7px) scale(.98); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes quiz-score-bump {
            50% { transform: scale(1.25); color: #2f8750; }
        }
        @keyframes quiz-score-float {
            to { opacity: 0; transform: translateY(-14px); }
        }
        @media (max-width: 480px) {
            .quiz-audio-controls {
                right: 10px;
                bottom: 10px;
            }
        }
    `;

    panel.className = "quiz-audio-controls";
    panel.setAttribute("aria-label", "Quiz audio controls");
    effectsButton.type = "button";
    musicButton.type = "button";
    panel.appendChild(effectsButton);
    panel.appendChild(musicButton);
    document.head.appendChild(style);
    document.body.appendChild(panel);

    function updateButtons() {
        effectsButton.textContent =
            `Effects: ${effectsEnabled ? "On" : "Off"}`;
        effectsButton.setAttribute(
            "aria-pressed",
            String(effectsEnabled)
        );
        musicButton.textContent =
            `Music: ${musicEnabled ? "On" : "Off"}`;
        musicButton.setAttribute(
            "aria-pressed",
            String(musicEnabled)
        );
    }

    function getAudioContext() {
        if (!AudioContextConstructor) return null;

        if (!audioContext) {
            audioContext = new AudioContextConstructor();
        }

        if (audioContext.state === "suspended") {
            audioContext.resume().catch(function() {
                effectsButton.title =
                    "Audio playback was blocked. Click an audio control to retry.";
                musicButton.title = effectsButton.title;
            });
        }

        return audioContext;
    }

    function playTone(
        frequency,
        startTime,
        duration,
        volume,
        output,
        waveform
    ) {
        const context = getAudioContext();
        if (!context) return;

        const oscillator = context.createOscillator();
        const gain = context.createGain();
        const endTime = startTime + duration;

        oscillator.type = waveform || "sine";
        oscillator.frequency.setValueAtTime(frequency, startTime);
        gain.gain.setValueAtTime(0.001, startTime);
        gain.gain.linearRampToValueAtTime(volume, startTime + 0.015);
        gain.gain.exponentialRampToValueAtTime(
            0.001,
            Math.max(startTime + 0.025, endTime)
        );
        oscillator.connect(gain);
        gain.connect(output || context.destination);
        oscillator.start(startTime);
        oscillator.stop(endTime + 0.02);
    }

    function playNotes(notes, spacing, volume) {
        const context = getAudioContext();
        if (!context) return;

        const startTime = context.currentTime + 0.02;
        notes.forEach(function(note, index) {
            playTone(
                note,
                startTime + index * spacing,
                0.18,
                volume
            );
        });
    }

    function playClick() {
        if (!effectsEnabled) return;
        const context = getAudioContext();
        if (!context) return;
        playTone(560, context.currentTime + 0.01, 0.045, 0.035);
    }

    function playCalmNote(frequency, startTime, duration, volume) {
        const context = getAudioContext();
        if (!context) return;

        const oscillator = context.createOscillator();
        const overtone = context.createOscillator();
        const gain = context.createGain();
        const overtoneGain = context.createGain();
        const endTime = startTime + duration;

        oscillator.type = "sine";
        overtone.type = "sine";
        oscillator.frequency.setValueAtTime(frequency, startTime);
        overtone.frequency.setValueAtTime(frequency * 2.01, startTime);
        gain.gain.setValueAtTime(0.001, startTime);
        gain.gain.linearRampToValueAtTime(volume, startTime + 0.025);
        gain.gain.exponentialRampToValueAtTime(
            volume * 0.28,
            startTime + 0.42
        );
        gain.gain.exponentialRampToValueAtTime(0.001, endTime);
        overtoneGain.gain.value = 0.12;
        oscillator.connect(gain);
        overtone.connect(overtoneGain);
        overtoneGain.connect(gain);
        gain.connect(musicBus);
        oscillator.start(startTime);
        overtone.start(startTime);
        oscillator.stop(endTime + 0.02);
        overtone.stop(endTime + 0.02);
    }

    function scheduleMusicChord() {
        if (!musicEnabled) return;

        const arpeggios = [
            [
                261.63, 329.63, 392.00, 523.25,
                392.00, 329.63, 261.63
            ],
            [
                220.00, 261.63, 329.63, 440.00,
                329.63, 261.63, 220.00
            ],
            [
                174.61, 220.00, 261.63, 349.23,
                261.63, 220.00, 174.61
            ],
            [
                196.00, 246.94, 293.66, 392.00,
                293.66, 246.94, 196.00
            ]
        ];
        const context = getAudioContext();
        if (!context || !musicBus) return;

        const startTime = context.currentTime + 0.03;
        arpeggios[chordIndex].forEach(function(note, index) {
            playCalmNote(
                note,
                startTime + index * 0.72,
                1.4,
                0.075
            );
        });
        chordIndex = (chordIndex + 1) % arpeggios.length;
        musicTimer = window.setTimeout(scheduleMusicChord, 5200);
    }

    function startMusic() {
        const context = getAudioContext();
        if (!context) return;

        if (!musicBus) {
            musicBus = context.createGain();
            musicBus.gain.value = 0;
            musicBus.connect(context.destination);
        }

        musicBus.gain.setTargetAtTime(0.28, context.currentTime, 0.2);
        scheduleMusicChord();
    }

    function stopMusic() {
        if (musicTimer !== null) {
            window.clearTimeout(musicTimer);
            musicTimer = null;
        }

        if (musicBus && audioContext) {
            musicBus.gain.setTargetAtTime(
                0,
                audioContext.currentTime,
                0.08
            );
        }
    }

    if (!AudioContextConstructor) {
        effectsEnabled = false;
        effectsButton.disabled = true;
        musicButton.disabled = true;
        effectsButton.title = "Audio is not supported by this browser.";
        musicButton.title = effectsButton.title;
    }

    updateButtons();

    effectsButton.addEventListener("click", function() {
        effectsEnabled = !effectsEnabled;
        updateButtons();
        if (effectsEnabled) getAudioContext();
    });

    musicButton.addEventListener("click", function() {
        musicEnabled = !musicEnabled;
        updateButtons();
        if (musicEnabled) {
            startMusic();
        } else {
            stopMusic();
        }
    });

    document.addEventListener("click", function(event) {
        if (event.target.closest(
            ".option, .arrange-chip, .pixel, .answer-item, " +
            ".pixel-reset, .matching-select, #nextButton, " +
            "#previousButton, #submitButton, #hintButton"
        )) {
            playClick();
        }
    });

    document.addEventListener("visibilitychange", function() {
        if (document.hidden) {
            stopMusic();
        } else if (musicEnabled) {
            startMusic();
        }
    });

    window.quizAudio = {
        playAnswer: function(isCorrect) {
            if (!effectsEnabled) return;
            if (isCorrect) {
                playNotes([659.25, 830.61], 0.11, 0.055);
            } else {
                playNotes([293.66, 220.00], 0.12, 0.045);
            }
        }
    };

    function formatCorrectAnswer(answer) {
        if (Array.isArray(answer)) {
            return answer.map(formatCorrectAnswer).join(", ");
        }

        if (answer && typeof answer === "object") {
            return Object.entries(answer).map(function(entry) {
                return `${entry[0]}: ${formatCorrectAnswer(entry[1])}`;
            }).join("; ");
        }

        return String(answer ?? "");
    }

    window.quizFeedback = {
        clear: function() {
            const message = document.getElementById("quizAnswerFeedback");
            if (message) message.remove();

            document.querySelectorAll(".quiz-score-pop").forEach(function(pop) {
                pop.remove();
            });
        },
        showAnswer: function(
            isCorrect,
            correctAnswer,
            score,
            awardPoint
        ) {
            const answerArea = document.getElementById("answerArea");
            const activeCard = document.querySelector(".question-card.active");
            const anchor = answerArea || activeCard;
            if (!anchor) return;

            let message = document.getElementById("quizAnswerFeedback");
            if (!message) {
                message = document.createElement("div");
                message.id = "quizAnswerFeedback";
                message.className = "quiz-feedback-message";
                message.setAttribute("role", "status");
                message.setAttribute("aria-live", "polite");
            }

            anchor.insertAdjacentElement("afterend", message);
            message.className = isCorrect
                ? "quiz-feedback-message quiz-feedback-correct"
                : "quiz-feedback-message quiz-feedback-incorrect";

            if (isCorrect) {
                message.textContent = awardPoint === false
                    ? `Correct! Total score: ${score}`
                    : `Correct! +1 point - Total score: ${score}`;

                if (awardPoint !== false) {
                    const scoreDisplay = document.querySelector(
                        "#score, #topScore, #scorePreview"
                    );

                    if (scoreDisplay) {
                        scoreDisplay.classList.remove("quiz-score-bump");
                        void scoreDisplay.offsetWidth;
                        scoreDisplay.classList.add("quiz-score-bump");

                        const pop = document.createElement("span");
                        pop.className = "quiz-score-pop";
                        pop.setAttribute("aria-hidden", "true");
                        pop.textContent = "+1";
                        scoreDisplay.insertAdjacentElement("afterend", pop);
                        window.setTimeout(function() {
                            pop.remove();
                        }, 950);
                    }
                }
            } else {
                message.textContent =
                    `Not quite. Correct answer: ${formatCorrectAnswer(correctAnswer)}`;
            }

            anchor.querySelectorAll(".option").forEach(function(option) {
                const radio = option.querySelector('input[type="radio"]');
                const optionAnswer = radio
                    ? radio.value.trim()
                    : option.textContent.trim();
                const matchesAnswer =
                    optionAnswer.toLowerCase() ===
                    formatCorrectAnswer(correctAnswer).trim().toLowerCase();
                const selected = radio
                    ? radio.checked
                    : option.classList.contains("selected");

                if (matchesAnswer) {
                    option.classList.add("quiz-option-correct");
                } else if (selected) {
                    option.classList.add("quiz-option-incorrect");
                }

                if (radio) radio.disabled = true;
                if (option.tagName === "BUTTON") {
                    option.disabled = true;
                }
            });

            if (answerArea) {
                answerArea.querySelectorAll(
                    "input, select, button"
                ).forEach(function(control) {
                    control.disabled = true;
                });
                answerArea.querySelectorAll(".answer-item").forEach(
                    function(item) {
                        item.draggable = false;
                    }
                );
            }
        }
    };
})();
