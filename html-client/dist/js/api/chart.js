let leftChartCtx = document.getElementById("chartLeftCanva").getContext("2d");
let rightChartCtx = document.getElementById("chartRightCanva").getContext("2d");

let leftChart, rightChart;

$(document).ready(function () {
  // Initial function call when the page loads
  handleHistoricalParamsChange();
  handleForecastDistrictChange();

  // Attach event listeners to select inputs
  $("#district-selector").change(function () {
    handleHistoricalParamsChange();
    handleForecastDistrictChange();
  });

  $("#duration-selector").change(function () {
    handleHistoricalParamsChange();
    handleForecastDistrictChange();
  });
});

const getHistoricalData = (district) => {
  return fetch(`${SERVER_URL}/historical_data?district=${district}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      return plotHistoricalGraph(data);
    })
    .catch((err) => {
      console.error("Fetch error:", { err });
      return null;
    });
};

// const durations = ["weekly", "biweekly", "2 months"];

// const getHistoricalData = async (district, duration) => {
//   const response = await fetch(
//     `${SERVER_URL}/historical_data?district=${district}&duration=${duration}`
//   );
//   return response.json();
// };

// const fetchAllHistoricalData = async (district) => {
//   const promises = durations.map((duration) =>
//     getHistoricalData(district, duration)
//   );
//   const results = await Promise.all(promises);
//   plotHistoricalGraph(results);
//   return;
// };

const getForecastAqi = (district) => {
  return fetch(`${SERVER_URL}/forecast_data?district=${district}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      plotPredictionGraph(data);
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

const handleHistoricalParamsChange = () => {
  // Get the values from the select inputs
  const district = $("#district-selector").val();
  // Call the function with the current values
  if (district) {
    getHistoricalData(district);
    // fetchAllHistoricalData(district);
  }
};

const handleForecastDistrictChange = () => {
  const district = $("#district-selector").val();
  if (district) {
    getForecastAqi(district);
  }
};

const plotHistoricalGraph = (data) => {
  const dataFor7DaysBefore = data.forecast_7d.aqi;
  const dataFor14DaysBefore = data.forecast_14d.aqi;
  const dataFor2MonthsBefore = data.historical;
  const totalLength = dataFor2MonthsBefore.aqi.length;

  console.log({ data, totalLength });

  const datasets = [
    {
      label: "Actual",
      data: roundNullableData(dataFor2MonthsBefore.aqi),
      borderColor: "blue",
      fill: false,
    },
    {
      label: "14 days",
      data: roundNullableData(padList(dataFor14DaysBefore, totalLength)),
      borderColor: "yellow",
      fill: false,
    },
    {
      label: "7 days",
      data: roundNullableData(padList(dataFor7DaysBefore, totalLength)),
      borderColor: "green",
      fill: false,
    },
  ];

  if (leftChart) {
    leftChart.destroy();
  }

  leftChart = new Chart(leftChartCtx, {
    type: "line",
    data: {
      labels: dataFor2MonthsBefore.date.map(convertDateFormat),
      datasets,
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: false,
          min: 0,
          max: 500,
        },
      },
    },
  });
};

const plotPredictionGraph = (data) => {
  const { firstSection, secondSection, thirdSection } = divideArray(data.aqi);

  let groupedDatasets = [
    {
      label: "Model 1",
      data: roundNullableData(firstSection),
      borderColor: "green",
      fill: false,
    },
    {
      label: "",
      data: roundNullableData(secondSection),
      backgroundColor: "transparent",
      borderColor: "yellow",
      fill: false,
    },
    {
      label: "",
      data: roundNullableData(thirdSection),
      backgroundColor: "transparent",
      borderColor: "red",
      fill: false,
    },
  ];

  if (rightChart) {
    rightChart.destroy();
  }

  rightChart = new Chart(rightChartCtx, {
    type: "line",
    data: {
      labels: data.date.map(convertDateFormat),
      datasets: groupedDatasets,
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: (ctx) => "Prediction Data",
        },
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          min: 0,
          max: 500,
        },
        x: {
          beginAtZero: false,
        },
      },
    },
  });
};

const convertDateFormat = (dateStr) => {
  const date = new Date(dateStr);

  const day = date.getDate();
  const year = date.getFullYear().toString().slice(-2);

  const monthNames = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "June",
    "July",
    "Aug",
    "Sept",
    "Oct",
    "Nov",
    "Dec",
  ];
  const month = monthNames[date.getMonth()];

  return `${day}-${month}-${year}`;
};

const padList = (list, targetLength) => {
  const padding = Array(targetLength - list.length).fill(null);
  return [...padding, ...list];
};

const roundNullableData = (data) => {
  return data.map((d) => {
    if (!d) return d;
    else return Math.round(d);
  });
};
