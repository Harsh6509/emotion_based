const video = document.getElementById("video");
const captureBtn = document.getElementById("captureBtn");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const emotionSpan = document.getElementById("emotion");
const recommendBtn = document.getElementById("recommendBtn");
const statusDiv = document.getElementById("status");
const resultsSection = document.getElementById("results");
const iframeWrap = document.getElementById("iframe-wrap");

let stream;

// 🎥 Start camera
startBtn.onclick = async () => {
  stream = await navigator.mediaDevices.getUserMedia({ video: true });
  video.srcObject = stream;
  captureBtn.disabled = false;
  stopBtn.disabled = false;
  startBtn.disabled = true;
};

// 🛑 Stop camera
function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    startBtn.disabled = false;
    stopBtn.disabled = true;
    captureBtn.disabled = true;
  }
}
stopBtn.onclick = stopCamera;

// 📸 Capture emotion
captureBtn.onclick = async () => {
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);

  statusDiv.textContent = "Detecting emotion...";

  const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));
  const formData = new FormData();
  formData.append("image", blob, "capture.jpg");

  try {
    const res = await fetch("/predict", { method: "POST", body: formData });
    const data = await res.json();

    if (data.emotion) {
      emotionSpan.textContent = data.emotion;
      statusDiv.textContent = "Emotion detected!";
      recommendBtn.disabled = false;
    } else if (data.error === "no_face_detected") {
      statusDiv.textContent = "No face detected. Try again.";
    } else {
      statusDiv.textContent = "Error detecting emotion.";
    }
  } catch (err) {
    console.error(err);
    statusDiv.textContent = "Server error.";
  }
};

// 🎵 Recommend songs (this part is still simple)
recommendBtn.onclick = async () => {
  const emotion = emotionSpan.textContent;
  const lang = document.getElementById("lang").value || "english";
  const singer = document.getElementById("singer").value || "";
  const mood = document.getElementById("mood").value || "";

  statusDiv.textContent = "Fetching recommendations...";

  try {
    const res = await fetch("/recommend_songs", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ emotion, lang, singer, mood })
    });

    const data = await res.json();
    iframeWrap.innerHTML = `
<iframe width="100%" height="400"
  src="${data.url}"
  frameborder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowfullscreen>
</iframe>`;

    resultsSection.hidden = false;
    statusDiv.textContent = "";
  } catch (err) {
    console.error(err);
    statusDiv.textContent = "Error fetching recommendations.";
  }
};


// 🔄 Reset button
document.getElementById("clearBtn").addEventListener("click", function () {
  emotionSpan.textContent = "—";
  document.getElementById("lang").value = "";
  document.getElementById("singer").value = "";
  document.getElementById("mood").value = "";
  iframeWrap.innerHTML = "";
  resultsSection.hidden = true;
  stopCamera();
});
