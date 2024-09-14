const loadShapefile = (shapefilePath, district, map, pollutant = null) => {
  let content = "";
  if (pollutant) {
    content = `${district.district} <br /> ${pollutant} <br /> AQI: ${Math.round(
      district.aqi
    )}`;
  } else {
    content = `${district.district} <br /> AQI: ${Math.round(district.aqi)}`;
  }

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
                color: district.color || district.color_code,
                weight: 2,
                opacity: 0.7,
                fillOpacity: 0.5,
              };
            },
          })
            .bindPopup(function (layer) {
              return content;
            })
            .addTo(map);

          return source.read().then(process);
        })
      );
    });
};

// const loadShapefileOnSingleMap = (shapefilePath, district, map) => {
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
//           })
//             .bindPopup(function (layer) {
//               return `District name: ${district} <br /> AQI: ${district}`;
//             })
//             .addTo(map);
//           return source.read().then(process);
//         })
//       );
//     });
// };
