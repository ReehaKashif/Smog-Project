const getMapRanking = () => {
  return getCurrentTime()
    .then((time) => {
      if (!time) return null;

      return fetch(`${SERVER_URL}/map_ranking?time=${time}`).then(
        (response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        }
      );
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

// Fetch district data
getMapRanking()
  .then((districtData) => {
    // Initialize the map
    var map1 = L.map("map1").setView([0, 0], 2);
    var map2 = L.map("map2").setView([0, 0], 2);

    // Add Google Maps layer
    L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
      maxZoom: 20,
      subdomains: ["mt0", "mt1", "mt2", "mt3"],
    }).addTo(map1);

    L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
      maxZoom: 20,
      subdomains: ["mt0", "mt1", "mt2", "mt3"],
    }).addTo(map2);

    // Load Shapefiles for each district using the fetched data
    Promise.all(
      districtData.map_ranking.map((districtInfo) => {
        const formattedDistrict = districtInfo.district
          .replace(/_/g, " ") // Replace underscores with spaces
          .replace(/\s+/g, "_"); // Replace spaces with underscores

        const shapefilePath = `../../../shapefiles/${formattedDistrict}.shp`;
        return loadShapefile(shapefilePath, districtInfo.color, map1, map2);
      })
    )
      .then(() => {
        console.log("All Shapefiles loaded successfully");
      })
      .catch((error) => console.error("Error loading Shapefiles:", error));
  })
  .catch((error) => console.error("Error fetching district data:", error));
