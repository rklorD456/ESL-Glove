document.addEventListener('DOMContentLoaded', () => {
    // --- Get all HTML elements ---
    const container = document.getElementById('prediction-container');
    const gestureImage = document.getElementById('gesture-image');
    const gestureWord = document.getElementById('gesture-word');
    const confidenceText = document.getElementById('confidence-text');
    const confidenceBar = document.getElementById('confidence-bar');
    const historyList = document.getElementById('history-list');
    const speakButton = document.getElementById('speak-button');
    const themeToggle = document.getElementById('checkbox');
    const body = document.body;
    const sentenceDisplay = document.getElementById('sentence-display');
    const clearSentenceBtn = document.getElementById('clear-sentence-btn');
    const languageSelect = document.getElementById('language-select');
    const translationOutput = document.getElementById('translation-output');
    const statusIndicator = document.getElementById('status-indicator');

    // --- Global Variables ---
    let sentence = [];
    let sentenceTimer = null;
    const PAUSE_DURATION = 2500;
    const socket = io();

    // --- Main Prediction Handler ---
    socket.on('new_prediction', function(data) {
        updateStatus('Listening...', 'status-listening');
        clearTimeout(sentenceTimer);

        container.classList.remove('visible');
        setTimeout(() => {
            gestureImage.src = `/static/images/${data.gesture}.png`;
            gestureWord.textContent = data.gesture.toUpperCase();
            confidenceText.textContent = `Confidence: ${data.confidence}%`;
            confidenceBar.style.width = `${data.confidence}%`;

            const lastWordInSentence = sentence.length > 0 ? sentence[sentence.length - 1] : '';
            if (data.gesture !== lastWordInSentence) {
                sentence.push(data.gesture);
                updateSentenceDisplay();
            }
            
            updateHistory(data.gesture);
            container.classList.add('visible');

            setTimeout(() => {
                if(sentenceTimer) {
                    updateStatus('Paused, waiting to translate...', 'status-paused');
                }
            }, PAUSE_DURATION - 1000);

            sentenceTimer = setTimeout(() => {
                triggerTranslation();
            }, PAUSE_DURATION);

        }, 400);
    });

    // --- Main Functions ---
    function updateSentenceDisplay() {
        sentenceDisplay.textContent = sentence.join(' ');
    }
    
    clearSentenceBtn.addEventListener('click', () => {
        sentence = [];
        updateSentenceDisplay();
        translationOutput.textContent = '';
        clearTimeout(sentenceTimer);
        updateStatus('Idle', '');
    });

    async function triggerTranslation() {
        const text = sentence.join(' ');
        const lang = languageSelect.value;
        if (!text) {
            updateStatus('Idle', '');
            return;
        };

        updateStatus('Translating...', 'status-translating');
        try {
            const response = await fetch('/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, target_lang: lang })
            });
            const data = await response.json();
            if (data.translated_text) {
                translationOutput.textContent = data.translated_text;
                speak(data.translated_text, lang);
            } else {
                translationOutput.textContent = 'Translation failed.';
            }
        } catch (error) {
            translationOutput.textContent = 'Translation error.';
        } finally {
            setTimeout(() => updateStatus('Idle', ''), 2000);
        }
    }

    // --- Helper Functions ---
    function updateStatus(message, className) {
        statusIndicator.textContent = message;
        statusIndicator.className = 'status-indicator';
        if (className) {
            statusIndicator.classList.add(className);
        }
    }

    function updateHistory(gesture) {
        const li = document.createElement('li');
        li.textContent = gesture.charAt(0).toUpperCase() + gesture.slice(1);
        historyList.prepend(li);
        if (historyList.children.length > 5) {
            historyList.lastChild.remove();
        }
    }

    // *** THIS IS THE NEW, IMPROVED SPEAK FUNCTION ***
    function speak(text, lang = 'en') {
        if (!('speechSynthesis' in window) || !text) {
            return;
        }

        window.speechSynthesis.cancel(); // Cancel any previous speech

        const utterance = new SpeechSynthesisUtterance(text);
        
        // Get all available voices
        const voices = window.speechSynthesis.getVoices();
        
        // Find a voice that matches the desired language (e.g., 'ar-EG' for Arabic)
        const desiredVoice = voices.find(voice => voice.lang.startsWith(lang));
        
        // If a matching voice is found, use it
        if (desiredVoice) {
            utterance.voice = desiredVoice;
            console.log(`Using voice: ${desiredVoice.name}`); // For debugging
        } else {
            // Otherwise, just set the language and let the browser choose
            utterance.lang = lang;
            console.warn(`No voice found for language '${lang}'. Using browser default.`); // For debugging
        }
        
        window.speechSynthesis.speak(utterance);
    }

    // --- Event Listeners ---
    speakButton.addEventListener('click', () => speak(gestureWord.textContent, 'en'));

    languageSelect.addEventListener('change', triggerTranslation);

    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
        themeToggle.checked = true;
    }
    
    themeToggle.addEventListener('change', () => {
        body.classList.toggle('dark-mode');
        localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
    });

    window.onload = () => {
        container.classList.add('visible');
        updateStatus('Idle', '');
    };
});