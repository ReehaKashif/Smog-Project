// const shapeFiles = [
//   { path: "../../../shape-files/Attock.shp", color: "#7b68ee" },
//   { path: "../../../shape-files/Bahawalnagar.shp", color: "#ff4500" },
//   { path: "../../../shape-files/Gujrat.shp", color: "#32cd32" },
//   { path: "../../../shape-files/Hafizabad.shp", color: "#4682b4" },
//   { path: "../../../shape-files/Jhang.shp", color: "#ff6347" },
//   { path: "../../../shape-files/Jhelum.shp", color: "#20b2aa" },
//   { path: "../../../shape-files/Kasur.shp", color: "#daa520" },
//   { path: "../../../shape-files/Lahore.shp", color: "#ff69b4" },
//   { path: "../../../shape-files/Layyah.shp", color: "#8a2be2" },
//   { path: "../../../shape-files/Multan.shp", color: "#00ced1" },
//   { path: "../../../shape-files/Narowal.shp", color: "#7fff00" },
//   { path: "../../../shape-files/Okara.shp", color: "#ff8c00" },
//   { path: "../../../shape-files/Rahim_Yar_Khan.shp", color: "#00bfff" },
//   { path: "../../../shape-files/Sahiwal.shp", color: "#dc143c" },
//   { path: "../../../shape-files/Sargodha.shp", color: "#ff1493" },
//   { path: "../../../shape-files/Sheikhupura.shp", color: "#4b0082" },
//   { path: "../../../shape-files/Sialkot.shp", color: "#6a5acd" },
//   { path: "../../../shape-files/Toba_Tek_Singh.shp", color: "#b22222" },
//   { path: "../../../shape-files/Vehari.shp", color: "#228b22" },
// ];

// // Initialize the map
// var map1 = L.map("map1").setView([0, 0], 2);
// var map2 = L.map("map2").setView([0, 0], 2);

// // Add Google Maps layer
// L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
//   maxZoom: 20,
//   subdomains: ["mt0", "mt1", "mt2", "mt3"],
// }).addTo(map1);

// L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
//   maxZoom: 20,
//   subdomains: ["mt0", "mt1", "mt2", "mt3"],
// }).addTo(map2);

// // Function to load a single Shapefile
// function loadShapefile(shapefilePath, color) {
//   return fetch(shapefilePath)
//     .then((response) => response.arrayBuffer())
//     .then((arrayBuffer) => {
//       return shapefile.open(arrayBuffer).then((source) =>
//         source.read().then(function process(result) {
//           if (result.done) return;

//           const geojson = {
//             type: "Feature",
//             geometry: result.value.geometry,
//             properties: result.value.properties,
//           };

//           L.geoJSON(geojson, {
//             style: function () {
//               return {
//                 color: color,
//                 weight: 2,
//                 opacity: 0.7,
//                 fillOpacity: 0.5,
//               };
//             },
//           }).addTo(map1);

//           L.geoJSON(geojson, {
//             style: function () {
//               return {
//                 color: color,
//                 weight: 2,
//                 opacity: 0.7,
//                 fillOpacity: 0.5,
//               };
//             },
//           }).addTo(map2);

//           return source.read().then(process);
//         })
//       );
//     });
// }

// // Load all Shapefiles
// Promise.all(shapeFiles.map((file) => loadShapefile(file.path, file.color)))
//   .then(() => {
//     console.log("All Shapefiles loaded successfully");
//   })
//   .catch((error) => console.error("Error loading Shapefiles:", error));

// Function to load a single Shapefile
const loadShapefile = (shapefilePath, district, map1, map2) => {
  return fetch(shapefilePath)
    .then((response) => response.arrayBuffer())
    .then((arrayBuffer) => {
      return shapefile.open(arrayBuffer).then((source) =>
        source.read().then(function process(result) {
          if (result.done) return;

          const geojson = {
            type: "Feature",
            geometry: result.value.geometry,
            properties: result.value.properties,
          };

          L.geoJSON(geojson, {
            style: function () {
              return {
                color: district.color,
                weight: 2,
                opacity: 0.7,
                fillOpacity: 0.5,
              };
            },
          })
            .bindPopup(function (layer) {
              return `District name: ${district.district} <br /> AQI: ${district.aqi}`;
            })
            .addTo(map1);

          L.geoJSON(geojson, {
            style: function () {
              return {
                color: district.color,
                weight: 2,
                opacity: 0.7,
                fillOpacity: 0.5,
              };
            },
          })
          .bindPopup(function (layer) {
            return `District name: ${district.district} <br /> AQI: ${district.aqi}`;
          })
          .addTo(map2);

          return source.read().then(process);
        })
      );
    });
};
