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
