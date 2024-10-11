const calculateSourceContribution = (district) => {
  getDistrictPollutantData(district).then((data) => {
    console.log({ data });

    let totalSourcesContributionValues = {};
    let totalSourcesContributionPercentages = {};

    // if (source === "all") {
    //   for (const source of pollutantsSources) {
    //     const pollutantContribution = calculatePollutantContribution(source);
    //     totalSourcesContributionValues[source] = pollutantContribution;
    //     const sourceContributionPercentage =
    //       calculateSourceContributionPercentage(pollutantContribution);
    //     totalSourcesContributionPercentages[source] =
    //       sourceContributionPercentage;
    //   }
    // } else {

    const pollutantContribution = calculatePollutantContribution(source);
    const sourceContributionPercentage = calculateSourceContributionPercentage(
      pollutantContribution
    );
    totalSourcesContributionPercentages[source] = sourceContributionPercentage;

    return renderPollutantDataInTable(
      totalSourcesContributionValues,
      totalSourcesContributionPercentages
    );
  })
};

const calculatePollutantContribution = (source) => {
  let totalContribution = 0;

  for (const pollutant in pollutantsData) {
    let averageValue;
    const predictedValue = pollutantsData[pollutant].predictedValue;
    const averageSourceValue = pollutantsData[pollutant].sources[source];
    if (averageSourceValue.includes("-")) {
      const range = averageSourceValue.split("-").map(Number);
      averageValue = (range[0] + range[1]) / 2;
    } else {
      averageValue = Number(averageSourceValue);
    }
    const pollutantContribution = (predictedValue * averageValue) / 100;
    totalContribution += pollutantContribution;
  }
  return totalContribution;
};

const calculateSourceContributionPercentage = (sourceContribution) => {
  const totalPredictedValue = Object.values(pollutantsValues).reduce(
    (acc, value) => acc + value,
    0
  );
  return (sourceContribution / totalPredictedValue) * 100;
};

const renderPollutantDataInTable = (
  totalSourcesContributionValues,
  totalSourcesContributionPercentages
) => {
  let tableData = [];
  let tableHtml =
    '<table class="pollutant-table w-[300px]"><thead class="p-2"><tr class="p-2"><th>Source</th><th>Value</th><th>%</th></tr></thead><tbody>';
  for (const source of pollutantsSources) {
    let sourceName = source === "Miscellaneous" ? "Misc" : source;
    tableData.push({
      source: sourceName,
      value: Math.round(totalSourcesContributionValues[source]),
      "%": Math.round(totalSourcesContributionPercentages[source]) + "%",
    });

    tableHtml += `<tr class="p-2">
      <td>${source}</td>
      <td>${Math.round(totalSourcesContributionValues[source])}</td>
      <td>${Math.round(totalSourcesContributionPercentages[source])}%</td>
    </tr>`;
  }
  return tableHtml;
};



const getDistrictPollutantData = (district) => {
  return fetch(`${SERVER_URL}/current_pollutants?district=${district}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};
