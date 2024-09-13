const SERVER_URL = "https://smop-api.onrender.com/api";
// const SERVER_URL = "http://localhost:8000/api";

const getCurrentTime = () => {
  return fetch(SERVER_URL + "/pakistan_time", {
    headers: {
      "Content-Type": "application/json", // Add any headers if needed
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json(); // Returns a promise
    })
    .then((data) => {
      return data.pakistan_time; // Adjust this based on the actual structure of the response
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};

// Populate color palletes
const color_palette = [
  ["#00ff00", "#33ff00", "#66ff00", "#99ff00", "#ccff00", "#ffff00"],
  ["#ffcc00", "#ff9900", "#ff6600", "#ff3300", "#ff0000", "#e60000"],
  ["#cc0000", "#b30000", "#990000", "#800000", "#66ff33", "#99ff33"],
  ["#ccff33", "#ffff33", "#ffcc33", "#ff9933", "#ff6633", "#ff3333"],
  ["#e60033", "#cc0033", "#b30033", "#990033", "#80ff66", "#b3ff66"],
  ["#ccff66", "#ffff66", "#ffcc66", "#ff9966", "#ff6666", "#ff3333"],
];

const color_palette_labels = [
  "Very Low",
  "Low",
  "Medium Low",
  "Medium",
  "Medium High",
  "High",
];

const populateColorPallete = () => {
  for (let i = 0; i < color_palette.length; i++) {
    $("#color-palette").append(`
       <div class="pallete-container">
                    <div style="background-color: ${color_palette[i][0]}" class="pallete-item"></div>
                    <div style="background-color: ${color_palette[i][1]}" class="pallete-item"></div>
                    <div style="background-color: ${color_palette[i][2]}" class="pallete-item"></div>
                    <div style="background-color: ${color_palette[i][3]}" class="pallete-item"></div>
                    <div style="background-color: ${color_palette[i][4]}" class="pallete-item"></div>
                    <div style="background-color: ${color_palette[i][5]}" class="pallete-item"></div>
                  </div>
      `);
    $("#district-rankings-map-legend").append(`
                <div class="ranking-map-pallete-row">
                  <div class="ranking-map-pallete-label">${color_palette_labels[i]}</div>
                  <div class="ranking-map-pallete-container">
                    <div style="background-color: ${color_palette[i][0]}" class="ranking-map-pallete-item"></div>
                    <div style="background-color: ${color_palette[i][1]}" class="ranking-map-pallete-item"></div>
                    <div style="background-color: ${color_palette[i][2]}" class="ranking-map-pallete-item"></div>
                    <div style="background-color: ${color_palette[i][3]}" class="ranking-map-pallete-item"></div>
                    <div style="background-color: ${color_palette[i][4]}" class="ranking-map-pallete-item"></div>
                    <div style="background-color: ${color_palette[i][5]}" class="ranking-map-pallete-item"></div>
                  </div>
                </div>
      `);
  }

  $("#color-palette").append("<div class='clearfix'></div>");
  // $("#color-palette").append("<div class='clearfix'></div>");
};

populateColorPallete();

const divideArray = (dataArray) => {
  const firstSection = [];
  const secondSection = [];
  const thirdSection = [];

  // First section (first 7 days)
  for (let i = 0; i < dataArray.length; i++) {
    if (i < 7) {
      firstSection.push(dataArray[i]);
      secondSection.push(null);
      thirdSection.push(null);
    } else if (i < 14) {
      firstSection.push(null);
      secondSection.push(dataArray[i]);
      thirdSection.push(null);
    } else {
      firstSection.push(null);
      secondSection.push(null);
      thirdSection.push(dataArray[i]);
    }
  }

  secondSection[6] = firstSection[6];
  thirdSection[13] = secondSection[13];

  return {
    firstSection,
    secondSection,
    thirdSection,
  };
};
// Get current hour and display it
$(document).ready(function () {
  function updateTime() {
    const now = new Date();
    const currentHour = String(now.getHours()).padStart(2, "0");
    const currentMinute = String(now.getMinutes()).padStart(2, "0");
    const currentSecond = String(now.getSeconds()).padStart(2, "0");
    $("#current-hour").text(`${currentHour}:${currentMinute}:${currentSecond}`);
  }

  updateTime(); // Initial call to display time immediately
  setInterval(updateTime, 1000); // Update time every second
});
