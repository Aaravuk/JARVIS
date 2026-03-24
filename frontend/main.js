$(document).ready(function () {

  // --- 1. HUD INITIALIZATION & BOOT SEQUENCE ---

  const bootSequenceText = [
    "> STARK INDUSTRIES",
    "> MARK 6 PROTOTYPE",
    "> INITIALIZING CORE SYSTEMS...",
    "> BYPASSING FIREWALLS...",
    "> ARC REACTOR ONLINE",
    "> ESTABLISHING NEURAL UPLINK..."
  ];

  // Click Event for Initialization Overlay
  $("#InitOverlay").click(function() {
    // Optional: Play a power-up sound here if you have one
    // let audio = new Audio('assets/powerup.mp3'); audio.play();

    $(this).fadeOut(800, function() {
      $("#HUD-Wrapper").removeAttr("hidden");
      $("#Start").removeAttr("hidden"); // Show your existing loader
      startBootSequence();
    });
  });

  // Typewriter Effect Logic
  function startBootSequence() {
    let i = 0;
    const speed = 600; // Time between lines (milliseconds)
    const container = $("#boot-text");
    container.empty();

    function typeLine() {
      if (i < bootSequenceText.length) {
        // Append text with a typing cursor
        container.append(`<div>${bootSequenceText[i]}<span class="blinking">_</span></div>`);
        
        // Remove cursor from previous line
        if (i > 0) {
          container.children().eq(i-1).find('span').remove();
        }
        
        i++;
        setTimeout(typeLine, speed);
      } else {
        // Remove the final cursor
        container.children().last().find('span').remove();
        
        // TRIGGER PYTHON BACKEND
        setTimeout(() => {
          container.append("<div style='color:#00ff00;'>> READY.</div>");
          
          // Start the Python Face Auth and Welcome sequence
          eel.init()(); 
        }, 800);
      }
    }
    
    // Start typing
    typeLine();
  }


  // --- 2. EXISTING ANIMATIONS & SIRI WAVE ---

  $(".text").textillate({
    loop: true,
    speed: 1500,
    sync: true,
    in: {
      effect: "bounceIn",
    },
    out: {
      effect: "bounceOut",
    },
  });

  $(".siri-message").textillate({
    loop: true,
    sync: true,
    in: {
      effect: "fadeInUp",
      sync: true,
    },
    out: {
      effect: "fadeOutUp",
      sync: true,
    },
  });

  var siriWave = new SiriWave({
    container: document.getElementById("siri-container"),
    width: 940,
    style: "ios9",
    amplitude: "1",
    speed: "0.30",
    height: 200,
    autostart: true,
    waveColor: "#ff0000",
    waveOffset: 0,
    rippleEffect: true,
    rippleColor: "#ffffff",
  });


  // --- 3. EXISTING EVENT LISTENERS (MIC, KEYBOARD, CHAT) ---

  $("#MicBtn").click(function () {
    eel.play_assistant_sound();
    $("#Oval").attr("hidden", true);
    $("#SiriWave").attr("hidden", false);

    eel.takeAllCommands()();
  });

  function doc_keyUp(e) {
    // this would test for whichever key is 40 (down arrow) and the ctrl key at the same time
    if (e.key === "j" && e.metaKey) {
      eel.play_assistant_sound();
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      eel.takeAllCommands()();
    }
  }
  document.addEventListener("keyup", doc_keyUp, false);

  function PlayAssistant(message) {
    if (message != "") {
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      eel.takeAllCommands(message);
      $("#chatbox").val("");
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      console.log("Empty message, nothing sent."); // Log if the message is empty
    }
  }

  function ShowHideButton(message) {
    if (message.length == 0) {
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      $("#MicBtn").attr("hidden", true);
      $("#SendBtn").attr("hidden", false);
    }
  }

  $("#chatbox").keyup(function () {
    let message = $("#chatbox").val();
    console.log("Current chatbox input: ", message); // Log input value for debugging
    ShowHideButton(message);
  });

  $("#SendBtn").click(function () {
    let message = $("#chatbox").val();
    PlayAssistant(message);
  });

  $("#chatbox").keypress(function (e) {
    let key = e.which;
    if (key == 13) {
      let message = $("#chatbox").val();
      PlayAssistant(message);
    }
  });

});