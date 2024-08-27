$(document).ready(function () {
  // Initial function call when the page loads
  handleSelectChanges();

  // Attach event listeners to select inputs
  $("#district-selector, #duration-selector").change(function () {
    handleSelectChanges();
  });
});

const getHistoricalData = (district, duration) => {
  return getCurrentTime()
    .then((time) => {
      if (!time) return null;
      return fetch(
        `${SERVER_URL}/historical_data?time=${time}&district=${district}&duration=${duration}`
      )
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          // console.log({ data });
          Morris.Area({
            element: "district-chart",
            data,
            xkey: "date",
            ykeys: ["Aqi"],
            labels: ["Aqi"],
          }).on("click", function (i, row) {
            console.log(i, row);
          });
        });
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

const handleSelectChanges = () => {
  // Get the values from the select inputs
  const district = $("#district-selector").val();
  const duration = $("#duration-selector").val();
  // Call the function with the current values
  if (district && duration) {
    getHistoricalData(district, duration);
  }
};
