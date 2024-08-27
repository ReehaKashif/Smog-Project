let cachedData = null;
let cacheTime = null;
const CACHE_DURATION = 30 * 60 * 1000; // Cache duration in milliseconds (5 minutes)

document.addEventListener("DOMContentLoaded", () => {
  getAqiStatus();
  const now = new Date().getTime();

  if (cachedData && now - cacheTime < CACHE_DURATION) {
    // Use cached data if still valid
    processAndCacheData(cachedData);
  } else {
    // Fetch new data if cache is expired or not available
    getDistrictAqiColor();
  }
});

const districtsHTML = (data) => {
  return `<!-- BEST DISTRICT -->
<div class="col-lg-3 col-xs-6">
  <div class="small-box bg-ash-gray">
    <div class="inner">
      <p>
        Best District Name and AQI
        <a href="#">&#9900; &#9900; &#9900;</a>
      </p>
      <h3>
        ${data.best_district.district}
        <span>
          <i class="fa fa-long-arrow-up"></i>
          ${data.best_district.aqi}
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
        Worst District Name and AQI
        <a href="#">&#9900; &#9900; &#9900;</a>
      </p>
      <h3>
        ${data.worst_district.district}
        <span>
          <i class="fa fa-long-arrow-up"></i>
          ${data.worst_district.aqi}
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
        Highest Pollutant District
        <a href="#">&#9900; &#9900; &#9900;</a>
      </p>
      <h3>
        ${data.highest_pollutant}
        <span>
          <i class="fa fa-long-arrow-up"></i>
        </span>
      </h3>
    </div>
  </div>
</div>
<!-- CAUSE OF POLLUTANT -->
<div class="col-lg-3 col-xs-6">
  <div class="small-box bg-ash-gray">
    <div class="inner">
      <p>
        Cause of Pollutant
        <a href="#">&#9900; &#9900; &#9900;</a>
      </p>
      <h3>
        ${data.cause_of_pollutant}
        <span>
          <i class="fa fa-long-arrow-up"></i>
        </span>
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
          const html = districtsHTML(data);
          $("#aqi-status").html(html);
        });
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

// Function to get district AQI color
const getDistrictAqiColor = () => {
  return getCurrentTime()
    .then((time) => {
      if (!time) return null;

      return fetch(`${SERVER_URL}/districts_aqi_color?time=${time}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          processAndCacheData(data.districts_aqi_color);
        });
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

const processAndCacheData = (data) => {
  if (!data) return;

  // Extract district field and store in an array
  const districts = data.map((item) => item.district);

  // Sort districts alphabetically
  districts.sort((a, b) => a.localeCompare(b));

  // Update the cached data and cache time
  cachedData = data;
  cacheTime = new Date().getTime();

  districts.forEach((district) => {
    $("#district-selector").append(`<option>${district}</option>`);
  });
  $("#district-selector").val(districts[0]).trigger('change');
};
