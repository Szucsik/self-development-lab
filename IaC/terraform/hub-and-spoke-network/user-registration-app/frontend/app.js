// API_BASE_URL is injected at container startup into /config.js (see entrypoint.sh).
// Falls back to localhost:8000 for local development without Docker.
const API_BASE_URL = window.API_BASE_URL || "http://localhost:8000";

const form = document.getElementById("registration-form");
const resultBox = document.getElementById("result");
const submitButton = form.querySelector("button[type='submit']");

function showResult(message, isSuccess) {
  resultBox.textContent = message;
  resultBox.classList.remove("success", "error");
  resultBox.classList.add(isSuccess ? "success" : "error");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const username = document.getElementById("username").value.trim();
  const age = Number(document.getElementById("age").value);

  if (!username) {
    showResult("Please enter a username.", false);
    return;
  }

  submitButton.disabled = true;
  submitButton.textContent = "Submitting...";

  try {
    const response = await fetch(`${API_BASE_URL}/api/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, age }),
    });

    const data = await response.json();

    if (!response.ok) {
      showResult(data.detail || "Something went wrong.", false);
    } else {
      showResult(data.message, data.success);
      if (data.success) {
        form.reset();
      }
    }
  } catch (err) {
    showResult(
      "Could not reach the server. Is the backend running?",
      false
    );
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Submit";
  }
});
