document.addEventListener("DOMContentLoaded", function () {
    const map = L.map('map').setView([0, 0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Image Gallery Logic
    gallery = document.getElementById("gallery");
    var markerGroup = L.layerGroup();

    function loadImages(data) {
        if (markerGroup.getLayers().length != 0) { // Removes markers from map if they exist previously 
            console.log('MARKER GROUP HAS LAYERS!!')
            markerGroup.clearLayers(map);
        } 
        //dLength = data.length();
        data_preview = data.slice(0, 12); // Just get first 10 images to save memory
        console.log("#######Data inside loadImages#######:", data_preview); // Debugging output
        if (data_preview.length == 0) {
            alert("No images found. Expand radius");
        }
        data_preview.forEach(image => {
            const img = document.createElement("img");
            img.src = image.url;  // Correctly accessing the URL field
            img.alt = image.title || "Gallery Image";  // Use title if available
            const coords = JSON.parse(image.geom);
            console.log('Coordinates:', coords.coordinates); // Test with coords
            var marker = L.marker([coords.coordinates[1], coords.coordinates[0]]).addTo(markerGroup);
            markerGroup.addTo(map);
            img.addEventListener("click", () => openImageModal(image.url));  // Click event to enlarge image
            gallery.appendChild(img);
        });
    }

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