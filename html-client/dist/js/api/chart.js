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
      plotRightGraph(data.date, data.aqi);
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
  }
};

const handleForecastDistrictChange = () => {
  const district = $("#district-selector").val();
  if (district) {
    getForecastAqi(district);
  }
};



const plotLeftGraph = (labels, datasets) => {
  if (leftChart) {
    leftChart.destroy();
  }

  leftChart = new Chart(leftChartCtx, {
    type: "line",
    data: {
      labels: labels.map(convertDateFormat),
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


const plotRightGraph = (labels, datasets) => {
  const { firstSection, secondSection, thirdSection } = divideArray(datasets);
  let groupedDatasets = [
    {
      label: "Model 1",
      data: firstSection,
      borderColor: "green",
      fill: false,
    },
    {
      label: "Model 2",
      data: secondSection,
      borderColor: "yellow",
      fill: false,
    },
    {
      label: "Model 3",
      data: thirdSection,
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
      labels: labels.map(convertDateFormat),
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


const convertDateFormat = (dateStr) => {
  const [year, month, day] = dateStr.split("-");
  return `${day}-${year}-${month}`;
};
