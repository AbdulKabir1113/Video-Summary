document.getElementById("summarize-btn").addEventListener("click", function () {
  const summaryText = `
    <p>This is the first paragraph of the summary.</p>
    <p>This is the second paragraph of the summary.</p>
    <p>This is the third paragraph, added for testing dynamic resizing.</p>
  `;

  const transcriptText = `
    <p>This is the full transcript content, which dynamically matches the height of the summary box.</p>
    <p>Longer transcripts will ensure both boxes remain aligned.</p>
  `;

  // Show both boxes
  document.getElementById("summary-box").style.display = "block";
  document.getElementById("transcript-box").style.display = "block";

  // Show loader
  document.getElementById("loader").style.display = "block";
  document.getElementById("summary-text").style.display = "none";

  // Simulate a delay
  setTimeout(function () {
    document.getElementById("loader").style.display = "none";
    document.getElementById("summary-text").style.display = "block";
    document.getElementById("summary-text").innerHTML = summaryText;
    document.getElementById("transcript-text").innerHTML = transcriptText;

    syncHeights(); // Sync the heights
  }, 3000);
});

// Function to sync heights of both boxes
function syncHeights() {
  const summaryBox = document.getElementById("summary-box");
  const transcriptBox = document.getElementById("transcript-box");

  const maxHeight = Math.max(summaryBox.scrollHeight, transcriptBox.scrollHeight);
  summaryBox.style.height = maxHeight + "px";
  transcriptBox.style.height = maxHeight + "px";
}

// Optionally, call syncHeights on window resize to adjust if content changes
window.addEventListener('resize', syncHeights);
