// const SERVER_URL = "https://smop-api.onrender.com/api";
const SERVER_URL = "http://localhost:8000/api";

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
  ["#00FF00", "#19F719", "#32EF32", "#4BE74B", "#64DF64", "#7DD77D"],
  ["#96CF96", "#AFC7AF", "#C8BFC8", "#E1B7E1", "#FF9FFF", "#FF99E5"],
  ["#FF92CC", "#FF8CB2", "#FF8699", "#FF7F80", "#FF7966", "#FF734D"],
  ["#FF6C33", "#FF662A", "#FF6020", "#FF5917", "#FF5313", "#FF4C0F"],
  ["#FF460B", "#FF4007", "#FF3A03", "#FF3300", "#FF2D00", "#FF2600"],
  ["#FF2000", "#FF1A00", "#FF1400", "#FF0D00", "#FF0700", "#FF0000"],
];

const populateColorPallete = () => {
  for (colorGroup of color_palette) {
    $("#color-palette").append(`
       <div class="pallete-container">
                    <div style="background-color: ${colorGroup[0]}" class="pallete-item"></div>
                    <div style="background-color: ${colorGroup[1]}" class="pallete-item"></div>
                    <div style="background-color: ${colorGroup[2]}" class="pallete-item"></div>
                    <div style="background-color: ${colorGroup[3]}" class="pallete-item"></div>
                    <div style="background-color: ${colorGroup[4]}" class="pallete-item"></div>
                    <div style="background-color: ${colorGroup[5]}" class="pallete-item"></div>
                  </div>
      `);
  }

  $("#color-palette").append("<div class='clearfix'></div>");
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
