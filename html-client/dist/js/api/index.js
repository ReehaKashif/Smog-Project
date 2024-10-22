// const OLD_SERVER_URL = "https://smop-api.onrender.com/api";
// const SERVER_URL = "http://localhost:8000/api";
const SERVER_URL = "https://smog-server.onrender.com/api";

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
  ["#00FF00", "#24FF00", "#48FF00", "#6CFF00", "#90FF00", "#B4FF00"],
  ["#D8FF00", "#FCFF00", "#FFF500", "#FFEB00", "#FFE100", "#FFD700"],
  ["#FFCC00", "#FFC200", "#FFB800", "#FFAD00", "#FFA300", "#FF9900"],
  ["#FF8E00", "#FF8400", "#FF7A00", "#FF6F00", "#FF6500", "#FF5B00"],
  ["#FF5100", "#FF4600", "#FF3C00", "#FF3200", "#FF2800", "#FF1D00"],
  ["#FF1300", "#FF0900", "#FF0000", "#F50000", "#EB0000", "#E10000"],
];

const color_palette_labels = [
  "Low",
  "Medium Low",
  "Medium",
  "Medium High",
  "High",
  "Very High",
];

const populateColorPallete = () => {
  for (let i = 0; i < color_palette.length; i++) {
    $("#color-palette").append(`
        <div>
          <div class="">${color_palette_labels[i]}</div>
          <div class="pallete-container">
            <div style="background-color: ${
              color_palette[i][0]
            }" class="pallete-item h-8 lg:h-10"><span class="pl-4">${
      i === 0 ? "Lowest" : ""
    }</span></div>
            <div style="background-color: ${
              color_palette[i][1]
            }" class="pallete-item h-8 lg:h-10"></div>
            <div style="background-color: ${
              color_palette[i][2]
            }" class="pallete-item h-8 lg:h-10"></div>
            <div style="background-color: ${
              color_palette[i][3]
            }" class="pallete-item h-8 lg:h-10"></div>
            <div style="background-color: ${
              color_palette[i][4]
            }" class="pallete-item h-8 lg:h-10"></div>
            <div style="background-color: ${
              color_palette[i][5]
            }" class="pallete-item h-8 lg:h-10"><span class="pl-4">${
      i === color_palette.length - 1 ? "Highest" : ""
    }</span></div>
          </div>
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

    const currentDate = now.toLocaleDateString("en-US", {
      weekday: "short",
      year: "numeric",
      month: "short",
      day: "numeric",
    });
    $("#current-date").text(currentDate);
    $("#current-hour").text(`${currentHour}:${currentMinute}:${currentSecond}`);
  }

  updateTime(); // Initial call to display time immediately
  setInterval(updateTime, 1000); // Update time every second
});

const setLocalStorage = (key, value) => {
  localStorage.setItem(key, JSON.stringify(value));
};

const getLocalStorage = (key) => {
  const value = localStorage.getItem(key);
  if (value) {
    return JSON.parse(value);
  }
  return null;
};

// const color_palette = [
//   ["#00ff00", "#33ff00", "#66ff00", "#99ff00", "#ccff00", "#ffff00"],
//   ["#ffcc00", "#ff9900", "#ff6600", "#ff3300", "#ff0000", "#e60000"],
//   ["#cc0000", "#b30000", "#990000", "#800000", "#66ff33", "#99ff33"],
//   ["#ccff33", "#ffff33", "#ffcc33", "#ff9933", "#ff6633", "#ff3333"],
//   ["#e60033", "#cc0033", "#b30033", "#990033", "#80ff66", "#b3ff66"],
//   ["#ccff66", "#ffff66", "#ffcc66", "#ff9966", "#ff6666", "#ff3333"],
// ];
