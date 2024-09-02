$(document).ready(function () {
  // Initial function call when the page loads
  const map = L.map("forecastMap").setView([31.14711, 75.3412], 6);
  fetchPollutantDistrictsApi(map);

  // Attach event listeners to select inputs
  $("#pollutant-source-selector").change(function () {
    fetchPollutantDistrictsApi(map);
  });
});

// Fetch district data
const getMapAqi = () => {
  return fetch(`${SERVER_URL}/districts_aqi_color`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

getMapAqi()
  .then((districtData) => {
    // Initialize the map
    var map = L.map("map1").setView([31.14711, 75.3412], 6);

    // Add Google Maps layer
    L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
      maxZoom: 20,
      subdomains: ["mt0", "mt1", "mt2", "mt3"],
    }).addTo(map);

    // Load Shapefiles for each district using the fetched data
    Promise.all(
      districtData.districts_aqi_color.map((districtInfo) => {
        const formattedDistrict = districtInfo.district.replace(/\s+/g, "_"); // Replace spaces with underscores
        // .replace(/_/g, " ") // Replace underscores with spaces
        const shapefilePath = `./shapefiles/${formattedDistrict}.shp`;
        return loadShapefile(shapefilePath, districtInfo, map);
      })
    )
      .then(() => {
        console.log("All Shapefiles loaded successfully");
      })
      .catch((error) => console.error("Error loading Shapefiles:", error));
  })
  .catch((error) => console.error("Error fetching district data:", error));



// Fetch district data
const getMapRanking = () => {
  return fetch(`${SERVER_URL}/map_ranking`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

getMapRanking()
  .then((districtData) => {
    // Initialize the map
    var map = L.map("map2").setView([31.14711, 75.3412], 6);

    // Add Google Maps layer
    L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
      maxZoom: 20,
      subdomains: ["mt0", "mt1", "mt2", "mt3"],
    }).addTo(map);

    // Load Shapefiles for each district using the fetched data
    Promise.all(
      districtData.map_ranking.map((districtInfo) => {
        const formattedDistrict = districtInfo.district.replace(/\s+/g, "_"); // Replace spaces with underscores
        // .replace(/_/g, " ") // Replace underscores with spaces
        const shapefilePath = `./shapefiles/${formattedDistrict}.shp`;
        return loadShapefile(shapefilePath, districtInfo, map);
      })
    )
      .then(() => {
        console.log("All Shapefiles loaded successfully");
      })
      .catch((error) => console.error("Error loading Shapefiles:", error));
  })
  .catch((error) => console.error("Error fetching district data:", error));

const getPollutantDistricts = (source) => {
  return fetch(`${SERVER_URL}/pollutant_districts?pollutant_name=${source}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

const fetchPollutantDistrictsApi = (map) => {
  const source = $("#pollutant-source-selector").val();
  // Fetch district data
  getPollutantDistricts(source)
    .then((data) => {
      // Add Google Maps layer
      L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
        maxZoom: 20,
        subdomains: ["mt0", "mt1", "mt2", "mt3"],
      }).addTo(map);

      // Load Shapefiles for each district using the fetched data
      getDistrictAqiColor().then((d) => {
        Promise.all(
          data.districts.map((district) => {
            const formattedDistrict = district.replace(/\s+/g, "_");
            const shapefilePath = `./shapefiles/${formattedDistrict}.shp`;

            const currentDistrict = d.districts_aqi_color.filter(
              (data) => data.district === district
            )[0];

            let districtInfo = {
              district: currentDistrict["district"],
              color: currentDistrict["color_code"],
              aqi: currentDistrict["aqi"],
            };
            return loadShapefile(shapefilePath, districtInfo, map);
          })
        ).catch((error) => console.error("Error loading Shapefiles:", error));
      });
    })
    .catch((error) => console.error("Error fetching district data:", error));
};
