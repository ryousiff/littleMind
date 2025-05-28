document.getElementById("uploadForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const fileInput = document.getElementById("drawing");
  const resultBox = document.getElementById("result");
  const form = document.getElementById("uploadForm");
  const button = form.querySelector("button");

  if (!fileInput.files.length) return;

  // Add loading state
  button.innerHTML = `<span class="loading-spinner"></span>Analyzing...`;
  button.disabled = true;
  resultBox.innerHTML = "";

  const formData = new FormData();
  formData.append("drawing", fileInput.files[0]);

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    if (data.result) {
      resultBox.innerHTML = `<div class="success-icon">✔</div>${data.result}`;
    } else {
      resultBox.innerHTML = "Something went wrong. Please try again.";
    }
  } catch (err) {
    resultBox.innerHTML = "Error communicating with AI.";
  } finally {
    button.innerHTML = `Analyze`;
    button.disabled = false;
  }
  document.getElementById("resetBtn").addEventListener("click", function () {
  document.getElementById("uploadForm").reset();
  document.getElementById("result").innerHTML = "";
  const uploadBox = document.getElementById("uploadBox");
  uploadBox.classList.remove("has-file");
  uploadBox.querySelector(".upload-text").innerText = "Click or drag to upload";
  uploadBox.querySelector(".upload-subtext").innerText = "Supported: PNG, JPG";
});

});
