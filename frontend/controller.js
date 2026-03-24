// --- EXPOSE FUNCTIONS TO PYTHON IMMEDIATELY ---
eel.expose(hideLoader);
eel.expose(hideFaceAuth);
eel.expose(hideFaceAuthSuccess);
eel.expose(hideStart);
eel.expose(DisplayMessage);
eel.expose(ShowHood);
eel.expose(senderText);
eel.expose(receiverText);
eel.expose(showConsole); 

// --- UI TRANSITION FUNCTIONS ---

function DisplayMessage(message) {
    console.log("UI received message: " + message);
    $(".siri-message li:first").text(message);
    $(".siri-message").textillate("start");
}

function hideLoader() {
    $("#Loader").attr("hidden", true);
    $("#FaceAuth").attr("hidden", false);
}

function hideFaceAuth() {
    $("#FaceAuth").attr("hidden", true);
    $("#FaceAuthSuccess").attr("hidden", false);
}

function hideFaceAuthSuccess() {
    $("#FaceAuthSuccess").attr("hidden", true);
    $("#HelloGreet").attr("hidden", false);
}

function hideStart() {
    $("#Start").attr("hidden", true);
    setTimeout(function () {
        $("#Oval").addClass("animate__animated animate__zoomIn");
        $("#Oval").attr("hidden", false);
    }, 1000);
}

function ShowHood() {
    $("#Oval").attr("hidden", false);
    $("#SiriWave").attr("hidden", true);
}

function showConsole() {
    $("#JarvisConsole").fadeIn(1000).removeAttr("hidden");
}

// --- MESSAGING LOGIC ---

function senderText(message) {
    var chatBox = document.getElementById("chat-display"); 
    if (message && chatBox) {
        chatBox.innerHTML += `<div class="msg-user" style="color: #fff; margin-bottom: 10px;">> ${message}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

function receiverText(message) {
    var chatBox = document.getElementById("chat-display"); 
    if (message && chatBox) {
        chatBox.innerHTML += `<div class="msg-jarvis" style="color: #00ffff; margin-bottom: 15px; font-weight: bold;">JARVIS: ${message}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

// --- EVENT LISTENERS ---

$(document).ready(function () {
    // 1. Send Button Click
    $("#send-btn").click(function () {
        let text = $("#user-input").val();
        if (text.trim() !== "") {
            // Immediately show in UI to confirm button worked
            senderText(text);
            $("#user-input").val("");
            
            // Trigger Python Command (Non-blocking)
            eel.takeAllCommands(text); 
        }
    });

    // 2. Enter Key Support
    $("#user-input").keypress(function (e) {
        if (e.which == 13) { 
            e.preventDefault(); // Prevents page refresh in some browsers
            $("#send-btn").click(); 
        }
    });

    // 3. Mic Button Logic
    $("#mic-btn").click(function () {
        // Provide visual feedback immediately
        console.log("Mic activated...");
        eel.play_assistant_sound();
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        
        // Trigger voice recognition in Python
        eel.takeAllCommands()(); 
    });

    // 4. Image Handling Logic
    $("#file-upload").change(function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const base64Data = e.target.result;
                
                // Show in UI
                $("#chat-display").append(`<div class="msg-user" style="color: #ffeb3b;">> [UPLOADING: ${file.name}]</div>`);
                $("#chat-display").append(`<img src="${base64Data}" style="width:120px; border:1px solid #00ffff; margin: 10px 0; border-radius: 5px;">`);
                $("#chat-display").scrollTop($("#chat-display")[0].scrollHeight);

                // ACTIVATE: Send the file to Python for processing
                eel.process_file(base64Data, file.name); 
            };
            reader.readAsDataURL(file);
        }
    });
});

eel.expose(updateStatus);
function updateStatus(elementId, statusText, addClass = "") {
    let element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = statusText;
        if (addClass) {
            element.classList.add(addClass);
        } else {
            element.classList.remove("status-active");
        }
    }
}