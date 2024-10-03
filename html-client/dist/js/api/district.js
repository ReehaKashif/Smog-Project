let cachedData = null;
let cacheTime = null;
const CACHE_DURATION = 30 * 60 * 1000; // Cache duration in milliseconds (5 minutes)

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
      const aqiAverage = calculateAverageAQI(data.districts_aqi_color);
      renderAverageAQI(aqiAverage);
      return data;
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

const processAndCacheData = (data) => {
  if (!data) return;

  // Cache the data
  const districts = data.map((item) => item.district);
  districts.sort((a, b) => a.localeCompare(b));

  setLocalStorage("districtsData", data);

  // Render districts to the dropdowns
  districts.forEach((district) => {
    $("#district-selector").append(`<option>${district}</option>`);
    $("#header-district-selector").append(`<option>${district}</option>`);
  });
  $("#district-selector").val(districts[0]).trigger("change");
  const lahoreDistrictIndex = districts.findIndex(
    (district) => district.toLowerCase() === "lahore"
  );
  $("#header-district-selector")
    .val(districts[lahoreDistrictIndex])
    .trigger("change");
};

const calculateAverageAQI = (data) => {
  const aqiValues = data.map((item) => item.aqi);
  const sum = aqiValues.reduce((acc, curr) => acc + curr, 0);
  return Math.round(sum / aqiValues.length);
};

const renderAverageAQI = (aqiAverage) => {
  $("#aqi-average").text(`${aqiAverage}`);
  $("#aqi-average-meter").text(`${aqiAverage}`);
  $("#aqi-average-meter-neddle").css("--score", aqiAverage);
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
