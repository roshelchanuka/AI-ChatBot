// Support for running inside Streamlit's components/st.html iframes
const doc = window.parent.document || document;
const parentWin = window.parent || window;

// Cleanup old artifacts from previous runs to avoid "zombie" listeners
function cleanupOldSession() {
    const oldMic = doc.getElementById('mic-btn');
    if (oldMic) {
        console.log("Cleaning up old mic button...");
        oldMic.remove();
    }
    // Stop any existing speech synthesis from previous frames
    if (parentWin.speechSynthesis) parentWin.speechSynthesis.cancel();
}

if (!window.travelBotInitialized) {
    window.travelBotInitialized = true;
    cleanupOldSession();
    initVoiceFeatures();
}

function initVoiceFeatures() {
    console.log("TravelBot Voice Features Initializing...");
    
    // 1. Parallax Background (Optimized)
    doc.addEventListener('mousemove', (e) => {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;
        const app = doc.querySelector('.stApp');
        if (app) {
            app.style.background = `radial-gradient(circle at ${x * 100}% ${y * 100}%, #1e293b, #0f172a)`;
        }
    });

    // 2. Speech Recognition Setup
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || parentWin.SpeechRecognition || parentWin.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        console.warn("Speech Recognition not supported in this browser.");
    } else {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        let isRecording = false;

        // Inject Mic Button
        const injectInterval = setInterval(() => {
            const chatInput = doc.querySelector('[data-testid="stChatInput"]') || 
                            doc.querySelector('.stChatInput') ||
                            doc.querySelector('textarea[aria-label*="Ask"]')?.closest('div');
            
            // If we find the input and the button isn't there, OR if it's an old button
            const existingMic = doc.getElementById('mic-btn');
            if (chatInput && !existingMic) {
                console.log("Chat Input found, injecting fresh mic button...");
                const micBtn = doc.createElement('div');
                micBtn.id = 'mic-btn';
                micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
                
                const target = chatInput.querySelector('div') || chatInput;
                target.appendChild(micBtn);

                micBtn.onclick = (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    try {
                        if (!isRecording) {
                            recognition.start();
                            console.log("STT Started");
                        } else {
                            recognition.stop();
                            console.log("STT Stopped");
                        }
                    } catch (err) {
                        console.error("Recognition Start Error:", err);
                        // If it's already started, just reset state
                        isRecording = false;
                        micBtn.classList.remove('recording');
                    }
                };
            }
        }, 1000);

        recognition.onstart = () => {
            isRecording = true;
            doc.getElementById('mic-btn')?.classList.add('recording');
        };

        recognition.onend = () => {
            isRecording = false;
            doc.getElementById('mic-btn')?.classList.remove('recording');
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            isRecording = false;
            doc.getElementById('mic-btn')?.classList.remove('recording');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log("Speech Result:", transcript);
            const textarea = doc.querySelector('[data-testid="stChatInput"] textarea');
            if (textarea) {
                const nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(parentWin.HTMLTextAreaElement.prototype, "value").set;
                nativeTextAreaValueSetter.call(textarea, transcript);
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                
                setTimeout(() => {
                    textarea.dispatchEvent(new KeyboardEvent('keydown', { 
                        key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true 
                    }));
                }, 500);
            }
        };
    }

    // 3. Speech Synthesis (Output)
    // Prevent duplicate observers on the parent body
    if (parentWin._travelBotObserver) {
        parentWin._travelBotObserver.disconnect();
    }

    console.log("Setting up MutationObserver for bot-bubbles...");
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) {
                    const botBubbles = node.classList?.contains('bot-bubble') ? [node] : node.querySelectorAll?.('.bot-bubble');
                    if (botBubbles && botBubbles.length > 0) {
                        botBubbles.forEach(bubble => {
                            if (!bubble.classList.contains('spoken') && !bubble.classList.contains('typing-indicator')) {
                                console.log("New bot bubble detected");
                                bubble.classList.add('spoken');
                                setTimeout(() => speakText(bubble.innerText), 500);
                            }
                        });
                    }
                }
            });
        });
    });

    const body = doc.querySelector('.stApp') || doc.body;
    if (body) {
        observer.observe(body, { childList: true, subtree: true });
        parentWin._travelBotObserver = observer; // Store on parent to allow cleanup
    }

    // Interaction Unlock
    const unlockAudio = () => {
        const silent = new SpeechSynthesisUtterance(" ");
        silent.volume = 0;
        (parentWin.speechSynthesis || window.speechSynthesis).speak(silent);
        doc.removeEventListener('click', unlockAudio);
    };
    doc.addEventListener('click', unlockAudio);
}

function speakText(text) {
    const synth = parentWin.speechSynthesis || window.speechSynthesis;
    if (!synth) return;
    
    console.log(`[TTS] Speaking: ${text.substring(0, 30)}...`);
    try {
        synth.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 1.0;
        utterance.onstart = () => console.log("[TTS] Audio Started");
        utterance.onerror = (e) => console.error("[TTS] Audio Error", e);
        synth.speak(utterance);
    } catch (err) {
        console.error("[TTS] Failed", err);
    }
}

window.parent.showSuccessPopup = function(message) {
    const popup = doc.createElement('div');
    popup.className = 'success-popup';
    popup.innerHTML = `
        <i class="fa-solid fa-circle-check"></i>
        <span>${message}</span>
    `;
    doc.body.appendChild(popup);
    
    setTimeout(() => {
        popup.classList.add('fade-out');
        setTimeout(() => popup.remove(), 500);
    }, 4000);
};

