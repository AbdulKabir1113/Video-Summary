document.getElementById("summarize-btn").addEventListener("click", function () {
  // Show both boxes

  document.getElementById('generated_images').innerHTML="";
  document.getElementById("summary-box").style.display = "block";
  document.getElementById("summary").innerText="";
  document.getElementById('transcribed').innerText="";
  document.getElementById("transcript-box").style.display = "block";
  document.getElementById('frames_from_video').style.display = 'none';

});
async function submitForm(event) {
            document.getElementById("summarize-btn").disabled=true;

            event.preventDefault(); // Prevent default form submission
            document.getElementById('loader').style.display = 'block'; // Show loader
            document.getElementById('loader1').style.display = 'block'; // Show loader
            document.getElementById("summary-box").style.display = "block";
//            document.getElementById("summary-box").innerHTMl="";
            document.getElementById("transcript-box").style.display = "block";

            const formData = new FormData(event.target);
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            document.getElementById('loader').style.display = 'none'; // Hide loader
            document.getElementById('loader1').style.display = 'none';
            document.getElementById('frames_from_video').style.display = 'block';
            document.getElementById('transcribed').innerText= result.transcribed_text;
            document.getElementById('summary').innerText = result.result; // Display result
            const gallery = document.getElementById('generated_images');

            // Loop through the image paths and create img elements
            result.img_dir.forEach(imagePath => {
              const imgElement = document.createElement('img');
              imgElement.src = imagePath;  // Set the image source
              imgElement.alt = 'Image';    // Set alternative text for the image

              // Append the img element to the gallery div
              gallery.appendChild(imgElement);
            });

            document.getElementById("summarize-btn").disabled=false;

        }
// Function to sync heights of both boxes
//function syncHeights() {
//  const summaryBox = document.getElementById("summary-box");
//  const transcriptBox = document.getElementById("transcript-box");
//
//  const maxHeight = Math.max(summaryBox.scrollHeight, transcriptBox.scrollHeight);
//  summaryBox.style.height = maxHeight + "px";
//  transcriptBox.style.height = maxHeight + "px";
//}
function hideLoder(){
if(document.getElementById("summary-box").innerHTMl!=""){
    document.getElementById("loader").style.display = "none";

}
}

function displayImages(path) {
      const gallery = document.getElementById('generated_images');

      // Loop through the image paths and create img elements
      path.forEach(imagePath => {
        const imgElement = document.createElement('img');
        imgElement.src = imagePath;  // Set the image source
        imgElement.alt = 'Image';    // Set alternative text for the image

        // Append the img element to the gallery div
        gallery.appendChild(imgElement);
      });
    }
// Optionally, call syncHeights on window resize to adjust if content changes
window.addEventListener('resize', syncHeights);
window.addEventListener('hide',hideLoder)