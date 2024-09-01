var leftChartCtx = document.getElementById("chartLeftCanva").getContext("2d");
var rightChartCtx = document.getElementById("chartRightCanva").getContext("2d");

let leftChart, rightChart;

$(document).ready(function () {
  // Initial function call when the page loads
  handleSelectChanges();

  // Attach event listeners to select inputs
  $("#district-selector, #duration-selector").change(function () {
    handleSelectChanges();
  });
  $("#forecast-cause-selector").change(function () {
    handleCauseSelectChanges();
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
      plotLeftGraph(data.date, data.aqi);
      plotRightGraph(data.date, data.aqi);
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

const getForecastAqi = (district) => {
  return fetch(`${SERVER_URL}/forecast_data?district=${district}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      console.log({ data });
      plotForecastChart(data.date, data.aqi);
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

const handleCauseSelectChanges = () => {
  const district = $("#forecast-clause-selector").val();
  if (district) {
    getForecastAqi(district);
  }
};

const plotLeftGraph = (labels, datasets) => {
  console.log({ leftChart });
  if (leftChart) {
    leftChart.destroy();
  }

  leftChart = new Chart(leftChartCtx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Actual vs Prediction",
          data: datasets,
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
          max: Math.ceil(Math.max(...datasets)).valueOf(),
        },
      },
    },
  });
};

// const skipped = (ctx, value) =>
//   ctx.p0.skip || ctx.p1.skip ? value : undefined;
// const down = (ctx, value) =>
//   ctx.p0.parsed.y > ctx.p1.parsed.y ? value : undefined;

const plotRightGraph = (labels, datasets) => {
  const { firstSection, secondSection, thirdSection } = divideArray(datasets);
  // console.log({ firstSection, secondSection, thirdSection });
  let groupedDatasets = [
    {
      label: "First 7 days",
      data: firstSection,
      borderColor: "green",
      fill: false,
    },
    {
      label: "Next 7 days",
      data: secondSection,
      borderColor: "yellow",
      fill: false,
    },
    {
      label: "The rest of the day",
      data: thirdSection,
      borderColor: "blue",
      fill: false,
    },
  ];

  if (rightChart) {
    rightChart.destroy();
  }

  rightChart = new Chart(rightChartCtx, {
    type: "line",
    data: {
      labels,
      datasets: groupedDatasets,
    },
    options: {
      scales: {
        y: {
          beginAtZero: false,
          min: 0,
          max: Math.ceil(Math.max(...datasets)).valueOf(),
        },
        x: {
          beginAtZero: false,
        },
      },
    },
  });
};

const plotForecastChart = (labels, datasets) => {
  var ctx = document.getElementById("forecastChart").getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Actual vs Prediction",
          data: datasets,
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
          max: 160,
        },
      },
    },
  });
};
