const calculateSourceContribution = (source = "all") => {
  let totalSourcesContributionValues = {};
  let totalSourcesContributionPercentages = {};

  if (source === "all") {
    for (const source of pollutantsSources) {
      const pollutantContribution = calculatePollutantContribution(source);
      totalSourcesContributionValues[source] = pollutantContribution;
      const sourceContributionPercentage =
        calculateSourceContributionPercentage(pollutantContribution);
      totalSourcesContributionPercentages[source] =
        sourceContributionPercentage;
    }
  } else {
    const pollutantContribution = calculatePollutantContribution(source);
    const sourceContributionPercentage = calculateSourceContributionPercentage(
      pollutantContribution
    );
    totalSourcesContributionPercentages[source] = sourceContributionPercentage;
  }
  return renderPollutantDataInTable(
    totalSourcesContributionValues,
    totalSourcesContributionPercentages
  );
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
    '<table class="pollutant-table"><thead><tr><th>Source</th><th>Value</th><th>Percentage</th></tr></thead><tbody>';
  for (const source of pollutantsSources) {
    tableData.push({
      source,
      value: Math.round(totalSourcesContributionValues[source]),
      "%": Math.round(totalSourcesContributionPercentages[source]) + "%",
    });

    tableHtml += `<tr>
      <td>${source}</td>
      <td>${Math.round(totalSourcesContributionValues[source])}</td>
      <td>${Math.round(totalSourcesContributionPercentages[source])}%</td>
    </tr>`;
  }
  return tableHtml;
};
