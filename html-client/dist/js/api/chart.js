var leftChartCtx = document.getElementById("chartLeftCanva").getContext("2d");
var rightChartCtx = document.getElementById("chartRightCanva").getContext("2d");

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

const getHistoricalData = (district, duration) => {
  return fetch(
    `${SERVER_URL}/historical_data?district=${district}&duration=${duration}`
  )
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
  const duration = $("#duration-selector").val();
  // Call the function with the current values
  if (district && duration) {
    getHistoricalData(district, duration);
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
  // const dataFor7DaysBefore = data[0];
  // const dataFor14DaysBefore = data[1];
  // const dataFor2MonthsBefore = data[2];

  // const datasets = [
  //   {
  //     label: "Actual",
  //     data: dataFor2MonthsBefore.aqi,
  //     borderColor: "green",
  //     fill: false,
  //   },
  //   {
  //     label: "Prediction Model 1",
  //     data: padList(dataFor14DaysBefore.aqi, dataFor2MonthsBefore.aqi.length),
  //     borderColor: "yellow",
  //     fill: false,
  //   },
  //   {
  //     label: "Prediction Model 2",
  //     data: padList(dataFor7DaysBefore.aqi, dataFor2MonthsBefore.aqi.length),
  //     borderColor: "red",
  //     fill: false,
  //   },
  // ];

  if (leftChart) {
    leftChart.destroy();
  }

  leftChart = new Chart(leftChartCtx, {
    type: "line",
    data: {
      labels: data.date.map(convertDateFormat),
      datasets: [
        {
          label: "Actual",
          data: data.aqi,
          borderColor: "green",
          fill: false,
        },
      ],
    },
    options: {
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
  const { aqi, aqi_7_days_lag, aqi_14_days_lag, date } = data;
  // const { firstSection, secondSection, thirdSection } = divideArray(datasets);
  // console.log({ aqi, aqi_7_days_lag, aqi_14_days_lag, date });

  let groupedDatasets = [
    {
      label: "Model 1",
      data: aqi,
      borderColor: "green",
      fill: false,
    },
    {
      label: "Model 2",
      data: aqi_14_days_lag,
      borderColor: "yellow",
      fill: false,
    },
    {
      label: "Model 3",
      data: aqi_7_days_lag,
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
      labels: date.map(convertDateFormat),
      datasets: groupedDatasets,
    },
    options: {
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
