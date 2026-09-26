// =====================================================
// CONFIGURATION
// =====================================================

const API_URL = "http://127.0.0.1:8000";


// =====================================================
// GET ELEMENTS
// =====================================================

const loginPage =
    document.getElementById("login-page");

const registerPage =
    document.getElementById("register-page");

const chatPage =
    document.getElementById("chat-page");

const chatContainer =
    document.getElementById("chat-container");

const messageInput =
    document.getElementById("message-input");

const sendButton =
    document.getElementById("send-button");

const resumeFile =
    document.getElementById("resume-file");


// =====================================================
// SHOW LOGIN
// =====================================================

function showLogin() {

    loginPage.classList.remove("hidden");

    registerPage.classList.add("hidden");

    chatPage.classList.add("hidden");

}


// =====================================================
// SHOW REGISTER
// =====================================================

function showRegister() {

    loginPage.classList.add("hidden");

    registerPage.classList.remove("hidden");

    chatPage.classList.add("hidden");

}


// =====================================================
// SHOW CHAT
// =====================================================

function showChat() {

    loginPage.classList.add("hidden");

    registerPage.classList.add("hidden");

    chatPage.classList.remove("hidden");

}


// =====================================================
// ADD MESSAGE TO CHAT
// =====================================================

function addMessage(message, role) {

    const messageElement =
        document.createElement("div");

    messageElement.className =
        `message ${role}`;


    const avatar =
        document.createElement("div");

    avatar.className = "avatar";

    avatar.textContent =
        role === "user"
            ? "👤"
            : "🤖";


    const content =
        document.createElement("div");

    content.className =
        "message-content";


    const name =
        document.createElement("div");

    name.className =
        "message-name";

    name.textContent =
        role === "user"
            ? "You"
            : "AI Assistant";


    const bubble =
        document.createElement("div");

    bubble.className =
        "message-bubble";

    bubble.textContent =
        message;


    content.appendChild(name);

    content.appendChild(bubble);

    messageElement.appendChild(avatar);

    messageElement.appendChild(content);


    chatContainer.appendChild(
        messageElement
    );


    // Scroll to bottom

    chatContainer.scrollTop =
        chatContainer.scrollHeight;


    return messageElement;
}


// =====================================================
// LOADING MESSAGE
// =====================================================

function addLoadingMessage() {

    const messageElement =
        document.createElement("div");

    messageElement.className =
        "message assistant";


    const avatar =
        document.createElement("div");

    avatar.className =
        "avatar";

    avatar.textContent = "🤖";


    const content =
        document.createElement("div");

    content.className =
        "message-content";


    const name =
        document.createElement("div");

    name.className =
        "message-name";

    name.textContent =
        "AI Assistant";


    const bubble =
        document.createElement("div");

    bubble.className =
        "message-bubble";


    const loading =
        document.createElement("div");

    loading.className =
        "loading";


    for (let i = 0; i < 3; i++) {

        const dot =
            document.createElement("span");

        dot.className =
            "loading-dot";

        loading.appendChild(dot);

    }


    bubble.appendChild(loading);

    content.appendChild(name);

    content.appendChild(bubble);

    messageElement.appendChild(avatar);

    messageElement.appendChild(content);

    chatContainer.appendChild(
        messageElement
    );


    chatContainer.scrollTop =
        chatContainer.scrollHeight;


    return messageElement;
}


// =====================================================
// LOGIN
// =====================================================

document
    .getElementById("login-form")
    .addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const email =
                document
                    .getElementById(
                        "login-email"
                    )
                    .value
                    .trim();


            const password =
                document
                    .getElementById(
                        "login-password"
                    )
                    .value;


            const errorElement =
                document.getElementById(
                    "login-error"
                );


            const loginButton =
                document.getElementById(
                    "login-button"
                );


            errorElement.textContent =
                "";


            loginButton.disabled =
                true;

            loginButton.textContent =
                "Logging in...";


            try {

                const response =
                    await fetch(
                        `${API_URL}/login`,
                        {

                            method: "POST",

                            headers: {

                                "Content-Type":
                                    "application/json"

                            },

                            body:
                                JSON.stringify({

                                    email:
                                        email,

                                    password:
                                        password

                                })

                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    errorElement.textContent =
                        data.detail ||
                        "Invalid email or password.";

                    return;
                }


                // =====================================
                // SAVE LOGIN INFORMATION
                // =====================================

                localStorage.setItem(
                    "access_token",
                    data.access_token
                );


                localStorage.setItem(
                    "user_id",
                    data.user_id
                );


                localStorage.setItem(
                    "user_name",
                    data.name
                );


                localStorage.setItem(
                    "user_email",
                    data.email
                );


                // =====================================
                // SHOW CHAT
                // =====================================

                document.getElementById(
                    "user-name"
                ).textContent =
                    data.name;


                showChat();


                // Clear previous screen

                chatContainer.innerHTML = "";


                // Load history

                await loadChatHistory();


                // Focus input

                messageInput.focus();


            } catch (error) {

                console.error(
                    "Login error:",
                    error
                );


                errorElement.textContent =
                    "Unable to connect to the server.";

            } finally {

                loginButton.disabled =
                    false;

                loginButton.textContent =
                    "Login";

            }

        }
    );


// =====================================================
// REGISTER
// =====================================================

document
    .getElementById("register-form")
    .addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const name =
                document
                    .getElementById(
                        "register-name"
                    )
                    .value
                    .trim();


            const email =
                document
                    .getElementById(
                        "register-email"
                    )
                    .value
                    .trim();


            const password =
                document
                    .getElementById(
                        "register-password"
                    )
                    .value;


            const messageElement =
                document.getElementById(
                    "register-message"
                );


            const registerButton =
                document.getElementById(
                    "register-button"
                );


            messageElement.textContent =
                "";


            registerButton.disabled =
                true;

            registerButton.textContent =
                "Creating account...";


            try {

                const response =
                    await fetch(
                        `${API_URL}/register`,
                        {

                            method: "POST",

                            headers: {

                                "Content-Type":
                                    "application/json"

                            },

                            body:
                                JSON.stringify({

                                    name:
                                        name,

                                    email:
                                        email,

                                    password:
                                        password

                                })

                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    messageElement.style.color =
                        "#dc2626";

                    messageElement.textContent =
                        data.detail ||
                        "Registration failed.";

                    return;
                }


                messageElement.style.color =
                    "#16a34a";


                messageElement.textContent =
                    "Registration successful! " +
                    "Redirecting to login...";


                document
                    .getElementById(
                        "register-form"
                    )
                    .reset();


                setTimeout(
                    function () {

                        showLogin();

                        document
                            .getElementById(
                                "login-email"
                            )
                            .value =
                            email;

                    },
                    1500
                );


            } catch (error) {

                console.error(
                    "Registration error:",
                    error
                );


                messageElement.style.color =
                    "#dc2626";


                messageElement.textContent =
                    "Unable to connect to the server.";

            } finally {

                registerButton.disabled =
                    false;

                registerButton.textContent =
                    "Create Account";

            }

        }
    );


// =====================================================
// SEND CHAT MESSAGE
// =====================================================

async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (!message) {

        return;

    }


    const token =
        localStorage.getItem(
            "access_token"
        );


    if (!token) {

        alert(
            "Your session has expired. " +
            "Please login again."
        );

        logout();

        return;

    }


    // Display user message

    addMessage(
        message,
        "user"
    );


    // Clear input

    messageInput.value = "";


    // Disable send

    sendButton.disabled =
        true;


    // Loading

    const loadingMessage =
        addLoadingMessage();


    try {

        const response =
            await fetch(
                `${API_URL}/api/chat`,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Bearer ${token}`

                    },

                    body:
                        JSON.stringify({

                            message:
                                message

                        })

                }
            );


        const data =
            await response.json();


        // Remove loading

        loadingMessage.remove();


        if (
            response.status === 401
        ) {

            alert(
                "Your session has expired. " +
                "Please login again."
            );

            logout();

            return;

        }


        if (!response.ok) {

            addMessage(
                data.detail ||
                "Something went wrong.",
                "assistant"
            );

            return;

        }


        // Display AI response

        addMessage(
            data.response,
            "assistant"
        );


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        loadingMessage.remove();


        addMessage(
            "Unable to connect to the AI server. " +
            "Please make sure FastAPI is running.",
            "assistant"
        );


    } finally {

        sendButton.disabled =
            false;

        messageInput.focus();

    }

}


// =====================================================
// ENTER KEY
// =====================================================

messageInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


// =====================================================
// LOAD CHAT HISTORY
// =====================================================

async function loadChatHistory() {

    const token =
        localStorage.getItem(
            "access_token"
        );


    if (!token) {

        return;

    }


    try {

        const response =
            await fetch(
                `${API_URL}/api/chat/history`,
                {

                    method: "GET",

                    headers: {

                        "Authorization":
                            `Bearer ${token}`

                    }

                }
            );


        if (
            response.status === 401
        ) {

            logout();

            return;

        }


        const data =
            await response.json();


        if (!response.ok) {

            console.error(
                data.detail
            );

            return;

        }


        chatContainer.innerHTML = "";


        if (
            !data.messages ||
            data.messages.length === 0
        ) {

            showWelcomeMessage();

            return;

        }


        data.messages.forEach(
            function (message) {

                addMessage(
                    message.message,
                    message.role
                );

            }
        );


    } catch (error) {

        console.error(
            "History error:",
            error
        );

    }

}


// =====================================================
// WELCOME MESSAGE
// =====================================================

function showWelcomeMessage() {

    addMessage(
        "👋 Hello! Welcome to the AI Career Assistant.\n\n" +

        "I can help you with:\n" +

        "💻 Data Structures and Algorithms\n" +

        "☕ Java, Python, C and C++\n" +

        "🗄️ SQL and DBMS\n" +

        "📚 Technical interviews\n" +

        "🎯 HR interviews\n" +

        "📄 Resume analysis\n\n" +

        "You can also click 📎 to upload your " +
        "resume as PDF, JPG, JPEG or PNG.",
        "assistant"
    );

}


// =====================================================
// RESUME FILE SELECTION
// =====================================================

if (resumeFile) {

    resumeFile.addEventListener(
        "change",
        uploadResume
    );

}


// =====================================================
// RESUME UPLOAD
// =====================================================

async function uploadResume() {

    const file =
        resumeFile.files[0];


    if (!file) {

        return;

    }


    // ================================================
    // CHECK FILE TYPE
    // ================================================

    const allowedTypes = [

        "application/pdf",

        "image/png",

        "image/jpeg"

    ];


    if (
        !allowedTypes.includes(
            file.type
        )
    ) {

        alert(
            "Please upload a PDF, PNG, JPG or JPEG file."
        );


        resumeFile.value = "";


        return;

    }


    // ================================================
    // CHECK FILE SIZE
    // ================================================

    const maxSize =
        5 * 1024 * 1024;


    if (file.size > maxSize) {

        alert(
            "File size must be less than 5 MB."
        );


        resumeFile.value = "";


        return;

    }


    // ================================================
    // CHECK LOGIN
    // ================================================

    const token =
        localStorage.getItem(
            "access_token"
        );


    if (!token) {

        alert(
            "Please login before uploading a resume."
        );


        resumeFile.value = "";


        showLogin();


        return;

    }


    // ================================================
    // SHOW USER MESSAGE
    // ================================================

    addMessage(
        `📎 Uploaded resume: ${file.name}`,
        "user"
    );


    // ================================================
    // SHOW LOADING
    // ================================================

    const loadingMessage =
        addLoadingMessage();


    try {

        const formData =
            new FormData();


        formData.append(
            "file",
            file
        );


        // ============================================
        // SEND FILE
        // ============================================

        const response =
            await fetch(
                `${API_URL}/api/resume/analyze`,
                {

                    method: "POST",

                    headers: {

                        "Authorization":
                            `Bearer ${token}`

                    },

                    body:
                        formData

                }
            );


        const data =
            await response.json();


        // Remove loading

        loadingMessage.remove();


        // ============================================
        // TOKEN EXPIRED
        // ============================================

        if (
            response.status === 401
        ) {

            alert(
                "Your session has expired. " +
                "Please login again."
            );


            logout();


            return;

        }


        // ============================================
        // ERROR
        // ============================================

        if (!response.ok) {

            addMessage(
                data.detail ||
                "Resume analysis failed.",
                "assistant"
            );


            return;

        }


        // ============================================
        // SUCCESS
        // ============================================

        addMessage(
            data.analysis,
            "assistant"
        );


    } catch (error) {

        console.error(
            "Resume upload error:",
            error
        );


        loadingMessage.remove();


        addMessage(
            "❌ Unable to analyze the resume. " +
            "Please make sure the backend is running.",
            "assistant"
        );

    } finally {

        resumeFile.value = "";

    }

}


// =====================================================
// LOGOUT
// =====================================================

function logout() {

    localStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "user_id"
    );

    localStorage.removeItem(
        "user_name"
    );

    localStorage.removeItem(
        "user_email"
    );


    chatContainer.innerHTML = "";


    document.getElementById(
        "login-form"
    ).reset();


    document.getElementById(
        "login-error"
    ).textContent = "";


    showLogin();

}


// =====================================================
// CHECK LOGIN WHEN PAGE LOADS
// =====================================================

window.addEventListener(
    "DOMContentLoaded",
    async function () {

        const token =
            localStorage.getItem(
                "access_token"
            );


        const userName =
            localStorage.getItem(
                "user_name"
            );


        if (
            token &&
            userName
        ) {

            document.getElementById(
                "user-name"
            ).textContent =
                userName;


            showChat();


            await loadChatHistory();


        } else {

            showLogin();

        }

    }
);