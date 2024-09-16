let pollutantDistrictsMap = null;
let districtMap = null;
let rankingMap = null;

$(document).ready(function () {
  fetchPollutantDistrictsApi();

  // Attach event listeners to select inputs
  $("#pollutant-source-selector").change(function () {
    fetchPollutantDistrictsApi();
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
    if (districtMap) {
      districtMap.remove();
    }
    districtMap = L.map("map1").setView([30.5, 72.5], 7);

    // Add Google Maps layer
    L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
      maxZoom: 20,
      subdomains: ["mt0", "mt1", "mt2", "mt3"],
    }).addTo(districtMap);

    // Load Shapefiles for each district using the fetched data
    const districts = [
      {
        district: "aoi_punjab",
        aqi_name: "black",
        color_code: "#000000",
        aqi: 0,
      },
      ...districtData.districts_aqi_color,
    ];
    Promise.all(
      districts.map((districtInfo) => {
        const formattedDistrict = districtInfo.district.replace(/\s+/g, "_");
        const shapefilePath = `./shapefiles/${formattedDistrict}.shp`;
        return loadShapefile(shapefilePath, districtInfo, districtMap);
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
    if (rankingMap) {
      rankingMap.remove();
    }
    // Initialize the map
    rankingMap = L.map("map2").setView([30.5, 72.5], 7);

    // Add Google Maps layer
    L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
      maxZoom: 20,
      subdomains: ["mt0", "mt1", "mt2", "mt3"],
    }).addTo(rankingMap);

    console.log({districtData})

    // Load Shapefiles for each district using the fetched data
    const mapRankingData = [
      { district: "aoi_punjab", color: "#000000", aqi: 0 },
      ...districtData.map_ranking,
    ];
    Promise.all(
      mapRankingData.map((districtInfo) => {
        const formattedDistrict = districtInfo.district.replace(/\s+/g, "_"); // Replace spaces with underscores
        // .replace(/_/g, " ") // Replace underscores with spaces
        const shapefilePath = `./shapefiles/${formattedDistrict}.shp`;
        return loadShapefile(shapefilePath, districtInfo, rankingMap);
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

const sources_color = {
  Vehicle: "#ffa500",
  Industry: "#f2af2a",
  Construction: "#ff2600",
  Agriculture: "#36454f",
  "General Wasting": "#7a288a",
};

const fetchPollutantDistrictsApi = () => {
  const source = $("#pollutant-source-selector").val();
  // Fetch district data
  getPollutantDistricts(source)
    .then((data) => {
      if (pollutantDistrictsMap) {
        pollutantDistrictsMap.remove();
      }
      // Initial function call when the page loads
      pollutantDistrictsMap = L.map("forecastMap").setView([30.5, 72.5], 7);
      // Add Google Maps layer
      L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
        maxZoom: 20,
        subdomains: ["mt0", "mt1", "mt2", "mt3"],
      }).addTo(pollutantDistrictsMap);

      // Load Shapefiles for each district using the fetched data
      getDistrictAqiColor().then((d) => {
        const districts = ["aoi_punjab", ...data.districts];
        Promise.all(
          districts.map(async (district) => {
            const formattedDistrict = district.replace(/\s+/g, "_");
            const shapefilePath = `./shapefiles/${formattedDistrict}.shp`;

            const currentDistrict = d.districts_aqi_color.filter(
              (data) => data.district === district
            )[0];

            let districtInfo = {
              district:
                district === "aoi_punjab"
                  ? "Punjab"
                  : currentDistrict["district"],
              color: sources_color[source],
              aqi: district === "aoi_punjab" ? 0 : currentDistrict["aqi"],
            };

            return await loadShapefile(
              shapefilePath,
              districtInfo,
              pollutantDistrictsMap,
              source
            );
          })
        ).catch((error) => console.error("Error loading Shapefiles:", error));
      });
    })
    .catch((error) => console.error("Error fetching district data:", error));
};
