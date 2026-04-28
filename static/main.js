// Support for running inside Streamlit's components/st.html iframes
const doc = window.parent.document || document;

if (!window.travelBotInitialized) {
    window.travelBotInitialized = true;
    initVoiceFeatures();
}

function initVoiceFeatures() {
    console.log("TravelBot Voice Features Initializing...");
    
    // 1. Parallax Background
    document.addEventListener('mousemove', (e) => {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;
        const app = document.querySelector('.stApp');
        if (app) {
            app.style.background = `radial-gradient(circle at ${x * 100}% ${y * 100}%, #1e293b, #0f172a)`;
        }
    });

    // 2. Speech Recognition Setup
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.warn("Speech Recognition not supported.");
    } else {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        let isRecording = false;

        // Inject Mic Button
        const injectMic = setInterval(() => {
            const chatInput = doc.querySelector('[data-testid="stChatInput"]') || 
                            doc.querySelector('.stChatInput') ||
                            doc.querySelector('textarea[aria-label*="Ask"]')?.closest('div');
            
            if (chatInput && !doc.getElementById('mic-btn')) {
                console.log("Chat Input found, injecting mic...");
                const micBtn = doc.createElement('div');
                micBtn.id = 'mic-btn';
                micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
                
                const target = chatInput.querySelector('div') || chatInput;
                target.appendChild(micBtn);

                micBtn.onclick = () => {
                    if (!isRecording) recognition.start();
                    else recognition.stop();
                };
            }
        }, 1000);

        recognition.onstart = () => {
            isRecording = true;
            document.getElementById('mic-btn')?.classList.add('recording');
        };

        recognition.onend = () => {
            isRecording = false;
            document.getElementById('mic-btn')?.classList.remove('recording');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const textarea = doc.querySelector('[data-testid="stChatInput"] textarea');
            if (textarea) {
                textarea.value = transcript;
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                setTimeout(() => {
                    textarea.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
                }, 300);
            }
        };
    }

    // 3. Speech Synthesis (Output)
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) {
                    const botBubbles = node.classList?.contains('bot-bubble') ? [node] : node.querySelectorAll?.('.bot-bubble');
                    if (botBubbles) {
                        botBubbles.forEach(bubble => {
                            if (!bubble.classList.contains('spoken') && !bubble.classList.contains('typing-indicator')) {
                                bubble.classList.add('spoken');
                                speakText(bubble.innerText);
                            }
                        });
                    }
                }
            });
        });
    });

    const body = doc.querySelector('.stApp') || doc.body;
    observer.observe(body, { childList: true, subtree: true });
}

function speakText(text) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    window.speechSynthesis.speak(utterance);
}

