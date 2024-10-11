const pollutantsData = {
  PM10: {
    predictedValue: 13.75,
    sources: {
      Vehicles: "30-40",
      Industry: "20-30",
      Construction: "10-20",
      Agriculture: "10-20",
      Miscellaneous: "10-20",
    },
  },
  "PM2.5": {
    predictedValue: 9.5,
    sources: {
      Vehicles: "30-40",
      Industry: "20-30",
      Construction: "10-20",
      Agriculture: "10-20",
      Miscellaneous: "10-20",
    },
  },
  NO2: {
    predictedValue: 10.2,
    sources: {
      Vehicles: "50-60",
      Industry: "30-40",
      Construction: "0",
      Agriculture: "0",
      Miscellaneous: "0",
    },
  },
  CO: {
    predictedValue: 136,
    sources: {
      Vehicles: "50-60",
      Industry: "30-40",
      Construction: "0",
      Agriculture: "0",
      Miscellaneous: "0",
    },
  },
  O3: {
    predictedValue: 1.7,
    sources: {
      Vehicles: "50-60",
      Industry: "30-40",
      Construction: "0",
      Agriculture: "0",
      Miscellaneous: "0",
    },
  },
  SO2: {
    predictedValue: 1.4,
    sources: {
      Vehicles: "0",
      Industry: "40-50",
      Construction: "0",
      Agriculture: "0",
      Miscellaneous: "0",
    },
  },
  Dust: {
    predictedValue: 50,
    sources: {
      Vehicles: "0",
      Industry: "0",
      Construction: "30-40",
      Agriculture: "30-40",
      Miscellaneous: "20-30",
    },
  },
};

const pollutantsValues = {
  PM10: 13.75,
  "PM2.5": 9.5,
  NO2: 10.2,
  CO: 136,
  O3: 1.7,
  SO2: 1.4,
  Dust: 50,
};

const pollutantsSources = [
  "Vehicles",
  "Industry",
  "Construction",
  "Agriculture",
  "Miscellaneous",
];

const pollutantsKeys = Object.keys(pollutantsValues);

const pollutantsUnits = {
  Carbon_monoxide: "CO",
  Dust: "Dust",
  Nitrogen_dioxide: "NO2",
  Ozone: "O3",
  Pm_10: "PM10",
  Pm_25: "PM2.5",
  Sulphur_dioxide: "SO2",
};

const pollutantsUnitsKeys = Object.keys(pollutantsUnits);
