// DOM Elements
document.addEventListener("DOMContentLoaded", function () {
  const uploadForm = document.getElementById("upload-form");
  const imageUpload = document.getElementById("image-upload");
  const browseButton = document.getElementById("browse-button");
  const imagePreview = document.getElementById("image-preview");
  const preview = document.getElementById("preview");
  const removeImage = document.getElementById("remove-image");
  const analyzeButton = document.getElementById("analyze-button");
  const resultSection = document.getElementById("result-section");
  const resultContent = document.getElementById("result-content");
  const uploadZone = document.querySelector(".upload-zone");
  const imageUrl = document.getElementById("image-url");
  const fetchUrlButton = document.getElementById("fetch-url-button");

  // Track current input method (file or url)
  let currentInputMethod = null;
  let imageUrlValue = null;

  // Open file dialog when browse button is clicked
  browseButton.addEventListener("click", function () {
    imageUpload.click();
  });

  // Display preview when file is selected
  imageUpload.addEventListener("change", function () {
    if (this.files.length > 0) {
      currentInputMethod = "file";
      handleFileSelect(this.files[0]);
      // Clear URL input when file is selected
      imageUrl.value = "";
      imageUrlValue = null;
    }
  });

  // Handle URL fetch button
  fetchUrlButton.addEventListener("click", function () {
    const url = imageUrl.value.trim();
    if (url) {
      currentInputMethod = "url";
      fetchImageFromUrl(url);
      // Clear file input when URL is used
      imageUpload.value = "";
    } else {
      alert("Please enter a valid image URL");
    }
  });

  // Also allow pressing Enter in the URL field
  imageUrl.addEventListener("keyup", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      fetchUrlButton.click();
    }
  });

  // Remove selected image
  removeImage.addEventListener("click", function () {
    resetUpload();
  });

  // Handle form submission
  uploadForm.addEventListener("submit", function (e) {
    e.preventDefault();

    // Show loading state
    setLoadingState(true);

    // Create form data for submission
    const formData = new FormData(uploadForm);

    // Send to Flask backend
    fetch("/predict", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        // Display result based on response
        displayResult(data);
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while analyzing the image. Please try again.");
      })
      .finally(() => {
        // Reset loading state
        setLoadingState(false);
      });
  });

  // Fetch image from URL for preview
  function fetchImageFromUrl(url) {
    // Show loading state
    setLoadingState(true);

    // Create a new Image object to test loading
    const img = new Image();

    img.onload = function () {
      // Successfully loaded the image
      preview.src = url;
      imagePreview.classList.remove("hidden");
      analyzeButton.disabled = false;
      imageUrlValue = url;
      setLoadingState(false);
    };

    img.onerror = function () {
      // Failed to load the image
      alert(
        "Could not load image from the provided URL. Please check the URL and try again."
      );
      setLoadingState(false);
    };

    // Set the source to trigger loading
    img.src = url;
  }

  // Handle drag and drop functionality
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function highlight() {
    uploadZone.classList.add("border-indigo-500");
  }

  function unhighlight() {
    uploadZone.classList.remove("border-indigo-500");
  }

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
      currentInputMethod = "file";
      handleFileSelect(files[0]);
      // Clear URL input when file is dropped
      imageUrl.value = "";
      imageUrlValue = null;
    }
  }

  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    uploadZone.addEventListener(eventName, preventDefaults, false);
  });

  ["dragenter", "dragover"].forEach((eventName) => {
    uploadZone.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    uploadZone.addEventListener(eventName, unhighlight, false);
  });

  uploadZone.addEventListener("drop", handleDrop, false);

  // Function to handle file selection
  function handleFileSelect(file) {
    if (!file) return;

    // Check if file is an image
    if (!file.type.match("image.*")) {
      alert("Please select an image file (JPEG or PNG).");
      return;
    }

    // Check file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      alert("File size exceeds 5MB limit. Please select a smaller file.");
      return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
      preview.src = e.target.result;
      imagePreview.classList.remove("hidden");
      analyzeButton.disabled = false;
    };
    reader.readAsDataURL(file);
  }

  // Function to reset upload
  function resetUpload() {
    imageUpload.value = "";
    imageUrl.value = "";
    imageUrlValue = null;
    imagePreview.classList.add("hidden");
    analyzeButton.disabled = true;
    currentInputMethod = null;
  }

  // Function to set loading state
  function setLoadingState(isLoading) {
    if (isLoading) {
      analyzeButton.disabled = true;
      analyzeButton.innerHTML = '<span class="spinner"></span>Analyzing...';
    } else {
      // Only enable the button if there's an image selected
      analyzeButton.disabled =
        !(currentInputMethod === "file" && imageUpload.files.length > 0) &&
        !(currentInputMethod === "url" && imageUrlValue);
      analyzeButton.textContent = "Analyze Image";
    }
  }

  // Function to display result
  // This code snippet shows the updated displayResult function
  // to handle the new OpenAI analysis information

  function displayResult(result) {
    resultSection.classList.remove("hidden");

    let statusClass, statusIcon;

    if (result.error) {
      // Handle error case
      resultContent.innerHTML = `
      <div class="status-indicator status-positive">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <h4 class="result-title">Error</h4>
          <p>${result.error}</p>
        </div>
      </div>
    `;
      return;
    }

    // Determine status class and icon based on prediction
    switch (result.prediction) {
      case "Non-Cancerous":
        statusClass = "status-negative";
        statusIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>`;
        break;
      case "Cancerous":
        statusClass = "status-positive";
        statusIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>`;
        break;
      default:
        statusClass = "status-suspicious";
        statusIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>`;
    }

    const confidencePercentage = Math.round(result.confidence);

    // Show cancer type if available (from OpenAI analysis)
    let cancerTypeHTML = "";
    if (result.cancer_type && result.cancer_type !== "Unspecified") {
      cancerTypeHTML = `
      <div class="result-section">
        <h4 class="result-label">Cancer Type:</h4>
        <p>${result.cancer_type}</p>
      </div>
    `;
    }

    let areasOfConcernHTML = "";
    if (result.areasOfConcern && result.areasOfConcern.length > 0) {
      areasOfConcernHTML = `
      <div class="result-section">
        <h4 class="result-label">Areas of Concern:</h4>
        <ul class="result-list">
          ${result.areasOfConcern.map((area) => `<li>${area}</li>`).join("")}
        </ul>
      </div>
    `;
    }

    // Symptoms section (from OpenAI analysis)
    let symptomsHTML = "";
    if (result.symptoms && result.symptoms.length > 0) {
      symptomsHTML = `
      <div class="result-section">
        <h4 class="result-label">Common Symptoms:</h4>
        <ul class="result-list">
          ${result.symptoms.map((symptom) => `<li>${symptom}</li>`).join("")}
        </ul>
      </div>
    `;
    }

    // Risk factors section (from OpenAI analysis)
    let riskFactorsHTML = "";
    if (result.risk_factors && result.risk_factors.length > 0) {
      riskFactorsHTML = `
      <div class="result-section">
        <h4 class="result-label">Risk Factors:</h4>
        <ul class="result-list">
          ${result.risk_factors.map((factor) => `<li>${factor}</li>`).join("")}
        </ul>
      </div>
    `;
    }

    // OpenAI detailed analysis section
    let openAiAnalysisHTML = "";
    if (result.openai_analysis) {
      openAiAnalysisHTML = `
      <div class="openai-analysis">
        <h4>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Detailed AI Analysis
        </h4>
        <div class="analysis-content">
          ${result.openai_analysis.replace(/\n/g, "<br>")}
        </div>
      </div>
    `;
    }

    // Recommendation section
    let recommendationHTML = "";
    if (result.recommendation) {
      recommendationHTML = `
      <div class="result-section">
        <h4 class="result-label">Recommendation:</h4>
        <p>${result.recommendation}</p>
      </div>
    `;
    }

    // Build the complete result HTML
    resultContent.innerHTML = `
    <div class="status-indicator ${statusClass}">
      ${statusIcon}
      <div>
        <h4 class="result-title">Result: ${result.prediction}</h4>
        <p class="result-subtitle">Confidence: ${confidencePercentage}%</p>
      </div>
    </div>
    
    ${cancerTypeHTML}
    ${areasOfConcernHTML}
    ${symptomsHTML}
    ${riskFactorsHTML}
    ${recommendationHTML}
    ${openAiAnalysisHTML}
    
    <div class="result-disclaimer">
      <p><strong>Disclaimer:</strong> This tool provides a preliminary assessment only and is not a definitive diagnosis. Always consult with a healthcare professional.</p>
    </div>
  `;

    // Add fade-in animation
    resultContent.classList.add("fade-in");

    // Scroll to result section
    resultSection.scrollIntoView({ behavior: "smooth" });
  }

  // Mobile menu toggle
  const mobileMenuBtn = document.querySelector(".mobile-menu-btn");
  const mainNav = document.querySelector(".main-nav");

  if (mobileMenuBtn && mainNav) {
    mobileMenuBtn.addEventListener("click", function () {
      mainNav.style.display =
        mainNav.style.display === "flex" ? "none" : "flex";
    });
  }
});
