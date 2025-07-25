const dropdownMenu = document.querySelector(".dropdown-menu");
const dropdownButton = document.querySelector(".dropdown-button");

if (dropdownButton) {
  dropdownButton.addEventListener("click", () => {
    dropdownMenu.classList.toggle("show");
  });
}

// Upload Image
const photoInput = document.querySelector("#avatar");
const photoPreview = document.querySelector("#preview-avatar");
if (photoInput)
  photoInput.onchange = () => {
    const [file] = photoInput.files;
    if (file) {
      photoPreview.src = URL.createObjectURL(file);
    }
  };

// Scroll to Bottom
const chat = document.getElementById("room__box");
function scrollToBottom() {
  chat.scrollTop = chat.scrollHeight;
}

const sendingElement = document.getElementById("sending");

document.addEventListener("DOMContentLoaded", () => {
  const messagesElement = document.getElementById("room__conversation");
  const roomId = messagesElement.dataset.roomId;
  loadMessages(roomId);
});

async function loadMessages(roomId) {
  console.log("this is runnn", roomId);
  sendingElement.innerHTML = "Loading messages...";

  try {
    const res = await fetch(`/get-messages/${roomId}/`);
    const data = await res.json();

    if (data.success === true) {
      const box = document.getElementById("room__box");
      box.innerHTML = ""; // Clear existing content

      const participantsBox = document.getElementById("participants__list");
      participantsBox.innerHTML = ""; // Clear existing content

      const participantsCount = document.getElementById("participants_count");
      participantsCount.innerHTML = ""; // Clear existing content

      if (data.messages.length > 0) {
        data.messages.forEach((msg) => {
          const thread = document.createElement("div");
          thread.classList.add("thread");

          thread.innerHTML = `
            <div class="thread__top">
              <div class="thread__author">
                <a href="/profile/${msg.user.id}/" class="thread__authorInfo">
                  <div class="avatar avatar--small">
                    <img src="/static/base/assets/avatar.svg" />
                  </div>
                  <span>@${msg.user.first_name}</span>
                </a>
                <span class="thread__date">${msg.created}</span>
              </div>
            </div>
            <div class="thread__details">${msg.content}</div>
          `;

          box.appendChild(thread);
        });
      } else {
        box.innerHTML = `
        <div class="thread">
          <div class="thread__details">
            <h3>No Messages yet...</h3>
          </div>
        </div>
      `;
      }

      if (data.participants.length > 0) {
        const count = data.participants_count || 0;
        participantsCount.innerHTML = `(${count} Joined)`;

        data.participants.forEach((msg) => {
          const thread = document.createElement("a");
          thread.classList.add("participant");
          thread.href = "/profile/" + msg.id;

          thread.innerHTML = `
            <div class="avatar avatar--medium">
              <img src="/static/base/assets/avatar.svg" />
            </div>
            <p>
              ${msg.first_name[0].toUpperCase() + msg.first_name.slice(1)}
              <span>@${msg.first_name}</span>
            </p>
          `;

          participantsBox.appendChild(thread);
        });
      }

      console.log("done!");
      // Scroll on initial load
      scrollToBottom();
    } else {
      console.error("Failed to load messages", err);
    }
  } catch (err) {
    console.error("Failed to load messages", err);
  }

  sendingElement.innerHTML =
    'Add "@ai" to their message to invoke the AI assistant';
  sendingElement.style.color = "white";
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      if (cookie.trim().startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.split("=")[1]);
        break;
      }
    }
  }
  return cookieValue;
}

const form = document.getElementById("messagesForm");
const formButton = document.getElementById("form-button");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const dataUrl = form.dataset.url;
  const content = document.getElementById("message-input");
  const messagesElement = document.getElementById("room__conversation");
  const roomId = messagesElement.dataset.roomId;
  formButton.disabled = true;
  sendingElement.innerHTML = "Sending message...";

  try {
    const response = await fetch(dataUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ message: content.value }),
      credentials: "same-origin",
    });

    const data = await response.json();
    if (data.success) {
      loadMessages(roomId);
      document.getElementById("message-input").value = "";
    } else {
      console.log("Error success===");
      sendingElement.innerHTML = "An error occured, try again!";
      sendingElement.style.color = "red";
    }

    formButton.disabled = false;
  } catch (error) {
    console.log("Error===", error);
    sendingElement.innerHTML = "An error occured, try again!";
    sendingElement.style.color = "red";
  }
});
