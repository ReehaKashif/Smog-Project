const pollutantCauses = {
  Lahore: {
    "Construction-Intensive": 27,
    "Vehicle-Intensive": 26,
    Industrial: 18,
    Agricultural: 16,
    Miscellaneous: 13,
  },
  Rawalpindi: {
    "Vehicle-Intensive": 26,
    "Construction-Intensive": 25,
    Industrial: 18,
    Agricultural: 16,
    Miscellaneous: 15,
  },
  Faisalabad: {
    Industrial: 33,
    "Vehicle-Intensive": 21,
    "Construction-Intensive": 20,
    Agricultural: 15,
    Miscellaneous: 11,
  },
  Gujranwala: {
    Industrial: 32,
    "Vehicle-Intensive": 22,
    "Construction-Intensive": 21,
    Agricultural: 14,
    Miscellaneous: 11,
  },
  Sialkot: {
    Industrial: 31,
    "Vehicle-Intensive": 23,
    "Construction-Intensive": 21,
    Agricultural: 15,
    Miscellaneous: 10,
  },
  Multan: {
    "Vehicle-Intensive": 27,
    Agricultural: 24,
    Industrial: 22,
    "Construction-Intensive": 15,
    Miscellaneous: 12,
  },
  Sargodha: {
    Agricultural: 36,
    "Vehicle-Intensive": 18,
    Industrial: 19,
    "Construction-Intensive": 15,
    Miscellaneous: 12,
  },
  Bahawalpur: {
    Agricultural: 50,
    Miscellaneous: 12,
    Industrial: 19,
    "Vehicle-Intensive": 10,
    "Construction-Intensive": 9,
  },
  "Rahim Yar Khan": {
    Agricultural: 50,
    Miscellaneous: 16,
    "Vehicle-Intensive": 15,
    "Construction-Intensive": 10,
    Industrial: 9,
  },
  Sheikhupura: {
    Industrial: 32,
    "Vehicle-Intensive": 22,
    Agricultural: 16,
    "Construction-Intensive": 18,
    Miscellaneous: 12,
  },
  Kasur: {
    Industrial: 29,
    Agricultural: 22,
    Miscellaneous: 15,
    "Vehicle-Intensive": 19,
    "Construction-Intensive": 15,
  },
  Vehari: {
    Agricultural: 26,
    "Vehicle-Intensive": 25,
    Miscellaneous: 16,
    Industrial: 19,
    "Construction-Intensive": 14,
  },
  Khanewal: {
    Agricultural: 35,
    "Vehicle-Intensive": 23,
    Miscellaneous: 12,
    Industrial: 15,
    "Construction-Intensive": 15,
  },
  "Toba Tek Singh": {
    Agricultural: 34,
    "Vehicle-Intensive": 23,
    "Construction-Intensive": 15,
    Industrial: 15,
    Miscellaneous: 13,
  },
  Mianwali: {
    Agricultural: 34,
    "Vehicle-Intensive": 24,
    Miscellaneous: 13,
    Industrial: 16,
    "Construction-Intensive": 13,
  },
  Attock: {
    Agricultural: 26,
    "Vehicle-Intensive": 24,
    Miscellaneous: 18,
    "Construction-Intensive": 18,
    Industrial: 14,
  },
  Chakwal: {
    Agricultural: 25,
    Miscellaneous: 19,
    "Vehicle-Intensive": 18,
    "Construction-Intensive": 17,
    Industrial: 16,
  },
  Jhang: {
    Agricultural: 34,
    "Vehicle-Intensive": 23,
    Industrial: 19,
    "Construction-Intensive": 13,
    Miscellaneous: 11,
  },
  Chiniot: {
    Agricultural: 33,
    "Vehicle-Intensive": 24,
    Industrial: 19,
    "Construction-Intensive": 13,
    Miscellaneous: 11,
  },
  Okara: {
    Agricultural: 33,
    "Vehicle-Intensive": 24,
    Industrial: 19,
    "Construction-Intensive": 13,
    Miscellaneous: 11,
  },
  Pakpattan: {
    Agricultural: 34,
    "Vehicle-Intensive": 23,
    Industrial: 18,
    "Construction-Intensive": 13,
    Miscellaneous: 12,
  },
  "Dera Ghazi Khan": {
    Agricultural: 35,
    "Vehicle-Intensive": 24,
    Industrial: 20,
    Miscellaneous: 11,
    "Construction-Intensive": 10,
  },
  Rajanpur: {
    Agricultural: 35,
    "Vehicle-Intensive": 25,
    Industrial: 19,
    Miscellaneous: 11,
    "Construction-Intensive": 10,
  },
  Layyah: {
    Agricultural: 35,
    "Vehicle-Intensive": 25,
    Industrial: 19,
    "Construction-Intensive": 11,
    Miscellaneous: 10,
  },
  Muzaffargarh: {
    Agricultural: 34,
    "Vehicle-Intensive": 25,
    Industrial: 19,
    "Construction-Intensive": 12,
    Miscellaneous: 10,
  },
  Sahiwal: {
    Agricultural: 36,
    "Construction-Intensive": 24,
    "Vehicle-Intensive": 20,
    Industrial: 11,
    Miscellaneous: 9,
  },
  Narowal: {
    "Vehicle-Intensive": 31,
    Agricultural: 30,
    "Construction-Intensive": 20,
    Industrial: 11,
    Miscellaneous: 8,
  },
  Hafizabad: {
    Agricultural: 35,
    "Vehicle-Intensive": 25,
    Industrial: 21,
    "Construction-Intensive": 10,
    Miscellaneous: 9,
  },
  Gujrat: {
    Industrial: 30,
    Agricultural: 29,
    "Vehicle-Intensive": 25,
    "Construction-Intensive": 10,
    Miscellaneous: 6,
  },
  "Mandi Bahuddin": {
    Agricultural: 34,
    "Vehicle-Intensive": 28,
    "Construction-Intensive": 20,
    Industrial: 12,
    Miscellaneous: 6,
  },
  Khushab: {
    Agricultural: 35,
    Miscellaneous: 30,
    "Vehicle-Intensive": 25,
    Industrial: 5,
    "Construction-Intensive": 5,
  },
  Jhelum: {
    "Vehicle-Intensive": 30,
    Agricultural: 29,
    "Construction-Intensive": 20,
    Industrial: 15,
    Miscellaneous: 6,
  },
  Bhakkar: {
    Agricultural: 33,
    "Vehicle-Intensive": 28,
    "Construction-Intensive": 20,
    Industrial: 12,
    Miscellaneous: 7,
  },
  "Nankana Sahib": {
    Agricultural: 35,
    "Vehicle-Intensive": 30,
    Industrial: 20,
    "Construction-Intensive": 10,
    Miscellaneous: 5,
  },
  Lodhran: {
    Agricultural: 36,
    Miscellaneous: 28,
    "Vehicle-Intensive": 18,
    Industrial: 10,
    "Construction-Intensive": 8,
  },
};

const getAndRenderPollutantCauses = (districtName, districtAqi) => {
  const polluantCause = pollutantCauses[districtName];
  if (!polluantCause) {
    return `${districtName} current AQI is ${districtAqi}`;
  }

  return `
  ${districtName} current AQI is ${Math.round(districtAqi)}	<br />
  Construction-Intensive: ${
    polluantCause["Construction-Intensive"]
  }% Value: ${calculatePollutantCauseValue(
    districtAqi,
    polluantCause["Construction-Intensive"]
  )}	<br />
  Vehicle-Intensive: ${
    polluantCause["Vehicle-Intensive"]
  }%    Value: ${calculatePollutantCauseValue(
    districtAqi,
    polluantCause["Vehicle-Intensive"]
  )}	<br />
  Industrial: ${
    polluantCause["Industrial"]
  }%       Value:      ${calculatePollutantCauseValue(
    districtAqi,
    polluantCause["Industrial"]
  )}	<br />
  Agricultural: ${
    polluantCause["Agricultural"]
  }%         Value:   ${calculatePollutantCauseValue(
    districtAqi,
    polluantCause["Agricultural"]
  )}	<br />
  Miscellaneous: ${
    polluantCause["Miscellaneous"]
  }%  Value: ${calculatePollutantCauseValue(
    districtAqi,
    polluantCause["Miscellaneous"]
  )}
  `;
};

const calculatePollutantCauseValue = (districtAqi, causePercentage) => {
  return Math.round((districtAqi * causePercentage) / 100);
};
