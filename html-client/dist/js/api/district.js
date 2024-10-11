let cachedData = null;
let cacheTime = null;
const CACHE_DURATION = 30 * 60 * 1000; // Cache duration in milliseconds (5 minutes)
let proccessedData = false;
document.addEventListener("DOMContentLoaded", () => {
  getAqiStatus();
  getDistrictAqiColor();

  setInterval(() => {
    getDistrictAqiColor();
  }, 1 * 60 * 60 * 1000); // 1 hour
});

const districtsHTML = (data) => {
  return `<!-- BEST DISTRICT -->
<div class="col-lg-3 col-xs-6">
  <div class="small-box bg-ash-gray">
    <div class="inner">
      <p class="">
       <span> Best Air Quality </span>
        <a href="#">&#9900; &#9900; &#9900;</a>
      </p>
      <h3>
        ${data.best_district.district}
        <span class="text-4xl font-bold">
          ${data.best_district.aqi.toFixed(0)}
        </span>
      </h3>
    </div>
  </div>
</div>
<!-- WORST DISTRICT -->
<div class="col-lg-3 col-xs-6">
  <div class="small-box bg-ash-gray">
    <div class="inner">
      <p>
       <span> Worst Air Quality </span>
        <a href="#">&#9900; &#9900; &#9900;</a>
      </p>
      <h3>
        ${data.worst_district.district}
        <span style="color: red;">
          ${data.worst_district.aqi.toFixed(0)}
        </span>
      </h3>
    </div>
  </div>
</div>
<!-- HIGHEST POLLUTANT DISTRICT -->
<div class="col-lg-3 col-xs-6">
  <div class="small-box bg-ash-gray">
    <div class="inner">
      <p>
        <span> Highest Pollutant </span>
        <a href="#">&#9900; &#9900; &#9900;</a>
      </p>
      <h3>
        ${data.highest_pollutant}
      </h3>
    </div>
  </div>
</div>
<!-- CAUSE OF POLLUTANT -->
<div class="col-lg-3 col-xs-6">
  <div class="small-box bg-ash-gray">
    <div class="inner">
      <p>
        <span> Cause of Pollutant </span>
        <a href="#">&#9900; &#9900; &#9900;</a>
      </p>
      <h3>
        ${data.cause_of_pollutant}
      </h3>
    </div>
  </div>
</div>`;
};

// Function to get AQI status
const getAqiStatus = () => {
  return getCurrentTime()
    .then((time) => {
      if (!time) return null;
      return fetch(`${SERVER_URL}/aqi_status?time=${time}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          // Update the content container with the new HTML
          // const html = districtsHTML(data);
          renderDistrictData(data);
          // $("#aqi-status").html(html);
        });
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

// Function to get district AQI color
const getDistrictAqiColor = () => {
  return fetch(`${SERVER_URL}/districts_aqi_color`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      processAndCacheData(data.districts_aqi_color);
      // const aqiAverage = calculateAverageAQI(data.districts_aqi_color);
      // renderAverageAQI(aqiAverage);
      return data;
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

const processAndCacheData = (data) => {
  if (proccessedData) return;
  if (!data) return;

  const districts = data.map((item) => item.district);
  districts.sort((a, b) => a.localeCompare(b));

  setLocalStorage("districtsData", data);

  const lahoreDistrictIndex = districts.findIndex(
    (district) => district.toLowerCase() === "lahore"
  );

  // Render districts to the dropdowns
  districts.forEach((district) => {
    $("#district-selector").append(`<option>${district}</option>`);
    $("#header-district-selector").append(`<option>${district}</option>`);
    $("#predition-district-selector").append(`<option>${district}</option>`);
  });
  $("#district-selector").val(districts[lahoreDistrictIndex]).trigger("change");
  $("#header-district-selector")
    .val(districts[lahoreDistrictIndex])
    .trigger("change");
  $("#predition-district-selector")
    .val(districts[lahoreDistrictIndex])
    .trigger("change");
  proccessedData = true;
};

const calculateAverageAQI = (data) => {
  const aqiValues = data.map((item) => item.aqi);
  const sum = aqiValues.reduce((acc, curr) => acc + curr, 0);
  return Math.round(sum / aqiValues.length);
};

const renderAverageAQI = (aqiAverage) => {
  $("#aqi-average").text(`${aqiAverage}`);
  $("#aqi-average-meter").text(`${aqiAverage}`);

  let angle;
  let rotationValue;

  // Calculate the rotation angle for the needle based on AQI ranges
  if (aqiAverage < 200) {
    // AQI less than 200: divide by 1.6, rotationValue is -90 + angle
    angle = aqiAverage / 1.6;
    rotationValue = -91 + angle;
  } else if (aqiAverage >= 201 && aqiAverage <= 300) {
    // AQI between 200 and 300: divide by 3.3, rotationValue is -30 + angle
    angle = aqiAverage / 3.3;
    rotationValue = -29 + angle;
  } else if (aqiAverage >= 301 && aqiAverage <= 500) {
    // AQI between 300 and 500: divide by 3.3, rotationValue is -15 + angle
    angle = aqiAverage / 6.6;
    rotationValue = +14 + angle;
  } else {
    // For AQI > 500, cap the rotation to 500 equivalent
    angle = 500 / 6.6;
    rotationValue = +14 + angle;
  }

  // Apply rotation to the needle
  $("#aqi-average-meter-neddle").css(
    "transform",
    `rotate(${rotationValue}deg)`
  );
};

const renderDistrictData = (data) => {
  $("#best-district-aqi").text(data.best_district.aqi.toFixed(0));
  $("#worst-district-aqi").text(data.worst_district.aqi.toFixed(0));
  $("#best-district-name").text(data.best_district.district);
  $("#worst-district-name").text(data.worst_district.district);
  $("#highest-pollutant-district").text(data.highest_pollutant);
  $("#cause-of-pollutant").text(data.cause_of_pollutant);
};

const handleHeaderDistrictChange = () => {
  const district = $("#header-district-selector").val();
  const cachedData = getLocalStorage("districtsData");
  if (cachedData) {
    const districtData = cachedData.filter(
      (item) => item.district === district
    )[0];
    renderAverageAQI(Math.round(districtData.aqi));
  }
};

$("#header-district-selector").change(function () {
  handleHeaderDistrictChange();
});
