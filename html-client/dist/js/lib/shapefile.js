const loadShapefile = (
  shapefilePath,
  district,
  map,
  popupContent = ""
) => {
  // let content = "";

  // if (mapType === "pollutantMap") {
  //   content = popupContent;
  // } else if (mapType === "rankingMap") {
  //   content = `${district.district} <br /> AQI: ${Math.round(
  //     district.aqi
  //   )} <br /> Rank: ${district.rank}`;
  // } else if (mapType === "districtAqi") {
  //   content = `${district.district} <br /> AQI: ${Math.round(district.aqi)}`;
  // } else {
  //   content = `${district.district} <br /> AQI: ${Math.round(district.aqi)}`;
  // }

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
              if (
                district.district === "Punjab" ||
                district.district === "aoi_punjab"
              ) {
                return {
                  color: "#000000",
                  stroke: true,
                  fill: false,
                  weight: 5,
                  opacity: 0.9,
                  fillOpacity: 0.1,
                };
              } else {
                return {
                  color: district.color || district.color_code,
                  stroke: true,
                  weight: 2,
                  opacity: 0.6,
                  fillOpacity: 0.5,
                };
              }
            },
          })
            .bindPopup(function (layer) {
              return popupContent;
            })
            .addTo(map);

          return source.read().then(process);
        })
      );
    });
};
