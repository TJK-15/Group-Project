document.addEventListener("DOMContentLoaded", function () {
    const map = L.map('map').setView([0, 0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Image Gallery Logic
    const gallery = document.getElementById("gallery");
    const loadMoreButton = document.createElement("button");
    loadMoreButton.innerText = "Load More";
    loadMoreButton.id = "load-more";
    loadMoreButton.style.display = "none";  // Initially hidden
    document.body.appendChild(loadMoreButton); // Append to body for positioning
    var markerGroup = L.layerGroup();

     // Create Image Counter
     const imageCounter = document.createElement("p");
     imageCounter.id = "image-counter";
     imageCounter.style.display = "none"; // Initially hidden
     document.querySelector(".gallery-container").appendChild(imageCounter);

    let allImages = [];
    let currentIndex = 0;
    const imagesPerPage = 12;

    function loadImages(data) {
        console.log("#######Data inside loadImages#######:", data); // Debugging output
        if (data.length == 0) { // Alert if no images are found
            alert("No images found. Expand radius");
        }
        allImages = data;
        imageTotal = data.length;
        currentIndex = 0;
        const imagesPerPage = 12;
        displayNextImages();
        loadMoreButton.style.display = allImages.length > imagesPerPage ? "block" : "none";
    }

    function displayNextImages() {
        if (markerGroup.getLayers().length != 0) { // Removes markers from map if they exist previously 
            console.log('MARKER GROUP HAS LAYERS!!')
            markerGroup.clearLayers(map);
        } 

        // Add to imageCounter
        if (currentIndex+imagesPerPage <= imageTotal) {
            imageCounter.innerText = `Showing ${currentIndex+1}-${currentIndex+imagesPerPage} of ${imageTotal}`;
            imageCounter.style.display = "block";
        } else if (imageTotal == 0) {
            imageCounter.style.display = "none";
        } else {
            imageCounter.innerText = `Showing ${currentIndex+1} - ${imageTotal}`;
            imageCounter.style.display = "block";
        }
        console.log('images being refreshed! currently displaying:', currentIndex + imagesPerPage, 'of total:', imageTotal);
        gallery.innerHTML = ''; // clear gallery
        const nextImageBatch = allImages.slice(currentIndex, currentIndex + imagesPerPage);
        nextImageBatch.forEach(image => {
            currentIndex = currentIndex + 1
            const img = document.createElement("img");
            img.src = image.url;  // Correctly accessing the URL field
            img.alt = image.title || "Gallery Image";  // Use title if available
            const coords = JSON.parse(image.geom);
            console.log('Coordinates:', coords.coordinates); // Test with coords
            var marker = L.marker([coords.coordinates[1], coords.coordinates[0]]).addTo(markerGroup);
            markerGroup.addTo(map);
            img.addEventListener("click", () => openImageModal(image.url));  // Click event to enlarge image
            gallery.appendChild(img);

            // Disable the "Load More" button if there are no more images to load
            if (currentIndex >= imageTotal) {
                loadMoreButton.disabled = true;
                loadMoreButton.style.display = "none"; // Optionally hide the button
            } else {
                loadMoreButton.disabled = false;
                loadMoreButton.style.display = "block"; // Ensure the button is visible
            }
        });
    }

    // Click on load more to load next images
    loadMoreButton.addEventListener("click", displayNextImages);

    // Open the enlarged image
    function openImageModal(imageUrl) {
        const modal = document.getElementById("image-modal");
        const modalImg = document.getElementById("modal-img");

        modal.style.display = "flex";
        modalImg.src = imageUrl;
    }

    // Close the modal when clicking outside the image
    document.getElementById("image-modal").addEventListener("click", function () {
        this.style.display = "none";
    });

    var cmarker;
    var circle;

    // On click function, gets lat, long, radius and creates API request
    map.on('click', function(e) {
        gallery.innerHTML = ''; // clear gallery
        var lat = e.latlng.lat.toFixed(6);
        var lng = e.latlng.lng.toFixed(6);
        var radius = document.getElementById('radius').value; // Radius is in meters
        var radiusText = radius + ' meters'; // Display the radius in meters
        
        if (cmarker) {
            cmarker.remove();
        }
        if (circle) {
            circle.remove();
        }
            
        cmarker = L.marker([lat, lng]).addTo(map)
            .bindPopup(`Lat: ${lat}, Lng: ${lng}<br>Radius: ${radiusText}`)
            .openPopup();
            
        circle = L.circle([lat, lng], {
            color: 'red',
            fillColor: '#f03',
             fillOpacity: 0.3,
            radius: radius
         }).addTo(map);
            
        document.getElementById('info').innerText = `Coordinates: ${lat}, ${lng} | Radius: ${radiusText}`;

        // Send data to Flask 
        fetch('/api/coordinates', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude: lat, longitude: lng, radius: radius })
            })
            .then(response => response.json())
            .then(data => loadImages(data))
            .then(data => console.log('Server response:', data))
            .catch(error => console.error('Error:', error));
            });

    // File Upload Logic
    document.getElementById('upload-button').addEventListener('click', function () {
        const fileInput = document.getElementById('file');
        const usernameInput = document.getElementById('username');
        const file = fileInput.files[0];
        const username = usernameInput.value;
        console.log('username is:', username)
    
        if (!file || !username) {
            alert('Please select a file and enter a username.');
            return;
        }

        // Get the current coordinates from the map marker
        const lat = cmarker ? cmarker.getLatLng().lat.toFixed(6) : null;
        const lng = cmarker ? cmarker.getLatLng().lng.toFixed(6) : null;

        if (!lat || !lng) {
            alert('Please click on the map to select a location.');
            return;
        }

        // Create FormData object to send file and metadata
        const formData = new FormData();
        console.log('script.js: Starting form data process!')
        formData.append('file', file);
        console.log('script.js: File appended!')
        formData.append('username', username);
        console.log('script.js: Username appended!')
        formData.append('latitude', lat);
        console.log('script.js: Lat appended!')
        formData.append('longitude', lng);
        console.log('script.js: Long appended!')
        console.log(formData)

        // Send the file and metadata to the Flask backend
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Upload response:', data);
            if (data.message) {
                alert(data.message); // Show success message
            } else if (data.error) {
                alert(data.error); // Show error message
            }
        })
        .catch(error => console.error('Error:', error));
    });
});