document.addEventListener("DOMContentLoaded", function () {
    const map = L.map('map').setView([0, 0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Image Gallery Logic
    const gallery = document.getElementById("gallery");
    const loadMoreButton = document.createElement("button");
    loadMoreButton.innerText = "Load More"; // Load more button for when the image array is greater than 12 images
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
        /**
         * This function loads the initial 12 images retrieved from a json string. 
         * 
         * Args:
         *  data (jsonString): A jsonstring containing image data
         * 
         * Processes:
         *  Reset current index to 0 
         *  Will run the displayNextImages function
         *  Load more button will appear if more than 12 images
         */
        console.log("#######Data inside loadImages#######:", data); // Debugging output
        allImages = data;
        imageTotal = data.length;
        currentIndex = 0;
        const imagesPerPage = 12;
        displayNextImages();
        loadMoreButton.style.display = allImages.length > imagesPerPage ? "block" : "none";
    }

    function displayNextImages() {
        /**
         * Displays the next batch of images in the gallery and updates the map with markers.
         * 
         * Args:
         *  allImages (array): Complete list of images received from the API
         *
         * Processes:
         *  Clears previous markers from the map.
         *  Updates the image counter with the current batch information.
         *  Loads and displays the next set of images (up to imagesPerPage at a time).
         *  Adds markers to the map based on image locations.
         *  Enables or disables the "Load More" button based on remaining images.
         *
         *
         * Side Effects:
         *  Modifies currentIndex by incrementing it for each new image added.
         *  Updates the UI elements (gallery, imageCounter, loadMoreButton).
         *  Updates map markers using Leaflet
         */

        if (markerGroup.getLayers().length != 0) { // Removes markers from map if they exist previously 
            console.log('MARKER GROUP HAS LAYERS!!')
            markerGroup.clearLayers(map);
        } 

        // Image counter display logic 
        if (currentIndex+imagesPerPage <= imageTotal) {
            imageCounter.innerText = `Showing ${currentIndex+1}-${currentIndex+imagesPerPage} of ${imageTotal}`;
            imageCounter.style.display = "block";
        } else if (imageTotal == 0) {
            imageCounter.innerText = `No images found. Consider expanding the radius.`;
            imageCounter.style.display = "block";
        } else {
            imageCounter.innerText = `Showing ${currentIndex+1} - ${imageTotal}`;
            imageCounter.style.display = "block";
        }
        console.log('images being refreshed! currently displaying:', currentIndex + imagesPerPage, 'of total:', imageTotal);
        gallery.innerHTML = ''; // clear gallery
        const nextImageBatch = allImages.slice(currentIndex, currentIndex + imagesPerPage);
        nextImageBatch.forEach(image => {
            currentIndex = currentIndex + 1;
            const img = document.createElement("img");
            img.src = image.url; 
            img.alt = image.title || "Gallery Image";  // Use title if available
            const coords = JSON.parse(image.geom);
            console.log('Coordinates:', coords.coordinates); // Test with coords
            L.marker([coords.coordinates[1], coords.coordinates[0]]).addTo(markerGroup); // Add marker at lng, lat to marker group
            markerGroup.addTo(map); // Add marker group to map
            img.addEventListener("click", () => openImageModal(image.url));  // Click event to enlarge image
            gallery.appendChild(img);

            // Disable the "Load More" button if there are no more images to load
            if (currentIndex >= imageTotal) {
                loadMoreButton.disabled = true;
                loadMoreButton.style.display = "none";
            } else {
                loadMoreButton.disabled = false;
                loadMoreButton.style.display = "block"; 
            }
        });
    }

    // Click on load more to load next images
    loadMoreButton.addEventListener("click", displayNextImages);

    function openImageModal(imageUrl) {
        /**
         * This function enlarges the clicked image by enabling the modal container. 
         * 
         * Args:
         *  imageUrl (str): url source of the image
         * 
         * Returns:
         *  Updates modal source to image source and enables viewing of modal on screen
         */
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

    map.on('click', function(e) {
        /**
         * This function will retrieve the latitude, longitude, and search radius upon the user clicking on the map. Then, we
         * create an API request to api/coordinates. 
         * 
         * Args: 
         *  lat (float): latitude value upon clicking on the map
         *  lng (float): longitude value upon clicking on the map
         *  radius (int): search radius in meters
         * 
         * Processes:
         *  1. Retrieve lat, lng, radius
         *  2. Add marker at location of click and popup of lat, lng, radius
         *  3. Sends data to API via json body of lat, lng, radius
         *  4. Sends json body to loadImages function
         * 
         * Returns:
         *  JSON body of latitude, longitude, and radius. 
         */
        gallery.innerHTML = ''; // clear gallery
        var lat = e.latlng.lat.toFixed(6);
        var lng = e.latlng.lng.toFixed(6);
        var radius = document.getElementById('radius').value; // Radius is in meters
        var radiusText = radius + ' meters'; // Display the radius in meters
        
        if (cmarker) {
            cmarker.remove(); // remove central marker if already exists
        }
        if (circle) {
            circle.remove(); // remove radius circle if already exists
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

        // Send data to API
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
        /**
         * This function sends an uploaded image and username to the Flask API. 
         * 
         * Args:
         *  fileInput: file inputted by user
         *  username (str): username inputted by user
         * 
         * Processes:
         *  1. Retrieves current lat, lng on the map
         *  2. Creates form data object to send file, username, lat, lng
         *  3. Sends form data to api/uploads
         * 
         * Returns:
         *  File, username, lat, lng in the form of a json string
         *  Data error message via browser alert
         */
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