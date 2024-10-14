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

        getWeatherData(districtInfo.district).then(({ temp, windspeed }) => {
          const popupContent = `<div class="flex gap-8">
        <span><strong>District:</strong> ${districtInfo.district}</span>
        <span><strong>AQI:</strong> ${Math.round(districtInfo.aqi)}</span>
        </div>
        <div class="flex gap-8">
        <span><strong>Temp:</strong> ${temp}</span>
        <span><strong>Windspeed:</strong> ${windspeed}</span>
        </div>`;

          return loadShapefile(
            shapefilePath,
            districtInfo,
            districtMap,
            popupContent
          );
        });
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

    const districts = districtData.map_ranking.map((data) => {
      const districtRank = color_palette.flat().indexOf(data.color);

      return {
        ...data,
        rank: districtRank + 1,
      };
    });

    // Load Shapefiles for each district using the fetched data
    const mapRankingData = [
      { district: "aoi_punjab", color: "#000000", aqi: 0 },
      ...districts,
    ];
    Promise.all(
      mapRankingData.map((districtInfo) => {
        const formattedDistrict = districtInfo.district.replace(/\s+/g, "_");
        const shapefilePath = `./shapefiles/${formattedDistrict}.shp`;

        getWeatherData(districtInfo.district).then(({ temp, windspeed }) => {
          const popupContent = `<div>
        <span><strong>Rank:</strong> ${districtInfo.rank}</span>
        <span><strong>District:</strong> ${districtInfo.district}</span>
        <span><strong>AQI:</strong> ${Math.round(districtInfo.aqi)}</span>
        </div>
        <div class="flex gap-8">
        <span><strong>Temp:</strong> ${temp}</span>
        <span><strong>Windspeed:</strong> ${windspeed}</span>
        </div>
        `;
          return loadShapefile(
            shapefilePath,
            districtInfo,
            rankingMap,
            popupContent
          );
        });
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

const fetchAllPollutantDistricts = () => {
  const sources = [
    "Vehicle",
    "Industry",
    "Construction",
    "Agriculture",
    "Miscellaneous",
  ];
  return Promise.all(sources.map((source) => getPollutantDistricts(source)))
    .then((results) => {
      return {
        Vehicle: results[0],
        Industry: results[1],
        Construction: results[2],
        Agriculture: results[3],
        Miscellaneous: results[4],
      };
    })
    .catch((err) => {
      console.error("Error fetching pollutant districts:", err);
      return null;
    });
};

const sources_color = {
  All: "#ee00fe",
  Vehicle: "#ffa500",
  Vehicles: "#ffa500",
  Industry: "#f2af2a",
  Construction: "#ff2600",
  Agriculture: "#36454f",
  Miscellaneous: "#7a288a",
};

const fetchPollutantDistrictsApi = () => {
  const source = $("#pollutant-source-selector").val();

  // if (source === "All") {
  //   fetchAllPollutantDistricts().then((allDistricts) => {
  //     const districts = [
  //       ...allDistricts.Vehicle.districts.map((district) => ({
  //         district,
  //         source: "Vehicle",
  //       })),

  //       ...allDistricts.Industry.districts.map((district) => ({
  //         district,
  //         source: "Industry",
  //       })),

  //       ...allDistricts.Construction.districts.map((district) => ({
  //         district,
  //         source: "Construction",
  //       })),

  //       ...allDistricts.Agriculture.districts.map((district) => ({
  //         district,
  //         source: "Agriculture",
  //       })),

  //       ...allDistricts.Miscellaneous.districts.map((district) => ({
  //         district,
  //         source: "Miscellaneous",
  //       })),
  //     ];

  //     plotAllPollutantDistricts(districts);
  //   });
  // } else {
  getPollutantDistricts(source).then((districtData) => {
    plotPollutantDistricts(districtData, source);
  });
  // }
};

// const plotAllPollutantDistricts = (data) => {
//   if (pollutantDistrictsMap) {
//     pollutantDistrictsMap.remove();
//   }
//   // Initial function call when the page loads
//   pollutantDistrictsMap = L.map("forecastMap").setView([31, 72.5], 7.45);
//   // Add Google Maps layer
//   L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
//     maxZoom: 20,
//     subdomains: ["mt0", "mt1", "mt2", "mt3"],
//   }).addTo(pollutantDistrictsMap);

//   // Load Shapefiles for each district using the fetched data
//   getDistrictAqiColor()
//     .then((d) => {
//       const districts = [{ district: "aoi_punjab", source: null }, ...data];
//       Promise.all(
//         districts.map(async ({ district, source }) => {
//           const formattedDistrict = district.replace(/\s+/g, "_");
//           const shapefilePath = `./shapefiles/${formattedDistrict}.shp`;

//           const currentDistrict = d.districts_aqi_color.filter(
//             (data) => data.district === district
//           )[0];

//           const { temp, windspeed } = await getWeatherData(district);
//           const { html, sourceWithHighestContribution } =
//             await calculateSourceContribution(district);

//           const popupContent = `<div class="flex gap-8"><span><strong>District:</strong> ${district}</span><span><strong>AQI:</strong> ${Math.round(
//             currentDistrict["aqi"]
//           )}</span></div>
//           <div class="flex gap-8"><span><strong>Temp:</strong> ${temp}</span><span><strong>Windspeed:</strong> ${windspeed}</span></div>
//          <hr />
//           <div>${html}</div>`;

//           let districtInfo = {
//             district:
//               district === "aoi_punjab"
//                 ? "Punjab"
//                 : currentDistrict["district"],
//             color:
//               district === "aoi_punjab"
//                 ? "#000000"
//                 : sources_color[sourceWithHighestContribution],
//             aqi: district === "aoi_punjab" ? 0 : currentDistrict["aqi"],
//           };

//           return await loadShapefile(
//             shapefilePath,
//             districtInfo,
//             pollutantDistrictsMap,
//             popupContent
//           );
//         })
//       ).catch((error) => console.error("Error loading Shapefiles:", error));
//     })
//     .catch((error) => console.error("Error fetching district data:", error));
// };

const plotPollutantDistricts = (data, source) => {
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
  getDistrictAqiColor()
    .then((d) => {
      const districts = ["aoi_punjab", ...data.districts];
      Promise.all(
        districts.map(async (district) => {
          const formattedDistrict = district.replace(/\s+/g, "_");
          const shapefilePath = `./shapefiles/${formattedDistrict}.shp`;

          const currentDistrict = d.districts_aqi_color.filter(
            (data) => data.district === district
          )[0];

          const { temp, windspeed } = await getWeatherData(district);
          const { sourceWithHighestContribution, html } =
            await calculateSourceContribution(district);

          const popupContent = `<div class="flex gap-8"><span><strong>District:</strong> ${district}</span><span><strong>AQI:</strong> ${Math.round(
            currentDistrict["aqi"]
          )}</span></div>
          <div class="flex gap-8"><span><strong>Temp:</strong> ${temp}</span><span><strong>Windspeed:</strong> ${windspeed}</span></div>
         <hr />
          <div>${html}</div>`;

          const districtColour =
            source === "All"
              ? sources_color[sourceWithHighestContribution]
              : sources_color[source];

          let districtInfo = {
            district:
              district === "aoi_punjab"
                ? "Punjab"
                : currentDistrict["district"],
            color: districtColour,
            aqi: district === "aoi_punjab" ? 0 : currentDistrict["aqi"],
          };

          return await loadShapefile(
            shapefilePath,
            districtInfo,
            pollutantDistrictsMap,
            popupContent
          );
        })
      ).catch((error) => console.error("Error loading Shapefiles:", error));
    })
    .catch((error) => console.error("Error fetching district data:", error));
};

const getWeatherData = async (district) => {
  const data = await getWeatherDataApi();
  const districtIndex = data.District.findIndex((d) => d === district);

  const temp = Math.round(data.Temperature[districtIndex]);
  const windspeed = Math.round(data.Wind_speed[districtIndex]);

  return {
    temp,
    windspeed,
  };
};

const getWeatherDataApi = () => {
  const weatherData = getLocalStorage("weather_data");
  if (weatherData) {
    return weatherData;
  }

  return fetch(`${SERVER_URL}/weather_data`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      setLocalStorage("weather_data", data);
      return data;
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};
